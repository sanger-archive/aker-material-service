var minDate = new Date(2010, 0, 1, 0, 0, 0, 0);
var maxDate = new Date(2017, 0, 1, 0, 0, 0, 0);
var delta = maxDate.getTime() - minDate.getTime();

var documentNumber = 1000;

var index = 0;

var materials_types = ['58209508c19205127005f298', '58209502c19205127005f297'];
var genders = ['male', 'female', 'unknown'];

var batch = new Array();

while(index < documentNumber) {
    var date_of_receipt = new Date(minDate.getTime() + Math.random() * delta);
    var value = Math.random();

    var document = {
        material_type: chooseRandom(materials_types),
        supplier_name: 'Supplier Name ' + index,
        donor_id: 'Donor ID ' + index,
        gender: chooseRandom(genders),
        scientific_name: 'Scientific Name ' + index,
        phenotype: 'Phenotype ' + (Math.round(index / 100) * 100),
        date_of_receipt: date_of_receipt.toUTCString(),
        meta: {
            'anything': 'i like ' + index
        }
    };

    batch.push(document);

    index++;
}

console.log(JSON.stringify(batch))

function chooseRandom(ary) {
    var index = Math.floor(Math.random() * ary.length);
    return ary[index];
}