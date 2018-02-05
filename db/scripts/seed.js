var minDate = new Date(2016, 0, 1, 0, 0, 0, 0);
var maxDate = new Date(2018, 0, 1, 0, 0, 0, 0);
var delta = maxDate.getTime() - minDate.getTime();

var tableName = 'materials';
tableName = db[tableName];

var documentNumber = 10000;

var batchNumber = 5 * 1000;

var start = new Date();

var batchDocuments = new Array();
var index = 0;

var genders = ['male', 'female', 'unknown', 'not applicable', 'mixed', 'hermaphrodite'];
var tissue_types = ['DNA/RNA', 'Blood', 'Saliva', 'Tissue', 'Cells', 'Lysed Cells'];

while(index < documentNumber) {
    var date_of_receipt = new Date(minDate.getTime() + Math.random() * delta);
    var value = Math.random();

    var document = {
        _id: generateUUID(),
        supplier_name: 'Supplier Name ' + index,
        donor_id: 'Donor ID ' + index,
        gender: chooseRandom(genders),
        tissue_type: chooseRandom(tissue_types),
        taxon_id: 9606,
        scientific_name: 'Homo sapiens',
        hmdmc: '10/123',
        phenotype: 'Phenotype ' + (Math.round(index / 100) * 100),
        date_of_receipt: date_of_receipt,
        available: true,
        owner_id: 'ac42@sanger.ac.uk',
        submitter_id: 'seed@sanger.ac.uk',
        is_tumour: false,
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

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}
