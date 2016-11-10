var numberOfSamples = n;

var tableName = table;

tableName = db[tableName];

var samples = tableName.aggregate([{$project: { _id: 1}}, {$sample: {size: numberOfSamples}}]);

var ids = samples.map(function(sample) { return sample._id.valueOf() });

ids.forEach(function(id) {
  print(id);
});