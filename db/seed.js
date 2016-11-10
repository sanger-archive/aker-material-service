var minDate = new Date(2010, 0, 1, 0, 0, 0, 0);
var maxDate = new Date(2017, 0, 1, 0, 0, 0, 0);
var delta = maxDate.getTime() - minDate.getTime();

var tableName = table;
tableName = db[tableName];

var documentNumber = n;

var batchNumber = 5 * 1000;

var start = new Date();

var batchDocuments = new Array();
var index = 0;

var materials_types = ['58209508c19205127005f298', '58209502c19205127005f297'];
var genders = ['male', 'female', 'unknown'];

while(index < documentNumber) {
    var date_of_receipt = new Date(minDate.getTime() + Math.random() * delta);
    var value = Math.random();

    var document = {
        material_type: {
            _id: chooseRandom(materials_types)
        },
        supplier_name: 'Supplier Name ' + index,
        donor_id: 'Donor ID ' + index,
        gender: chooseRandom(genders),
        common_name: 'Common Name ' + index,
        phenotype: 'Phenotype ' + (Math.round(index / 100) * 100),
        date_of_receipt: date_of_receipt,
        meta: {
            'anything': 'i like ' + index
        }
    };

    batchDocuments[index % batchNumber] = document;

    if((index + 1) % batchNumber == 0) {
        tableName.insert(batchDocuments);
    }

    index++;

    if(index % 100000 == 0) {
        print('Inserted ' + index + ' documents.');
    }
}

print('Inserted ' + documentNumber + ' in ' + (new Date() - start)/1000.0 + 's');

function chooseRandom(ary) {
    var index = Math.floor(Math.random() * ary.length);
    return ary[index];
}