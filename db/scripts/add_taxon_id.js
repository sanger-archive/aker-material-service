/*
  Script to add a taxon_id value to the documents for change A181
 */

// Set the connection parameters
const HOST = 'localhost'
const PORT = '27017'
const DATABASE = 'materials'

// Connect to the db
const CONN = new Mongo(`${HOST}:${PORT}`)
let db = CONN.getDB(DATABASE)

// Get the number of records for each species
let totalMaterials = db.materials.count()

let numberOfHumans = db.materials.count(
  { 'scientific_name': /^homo sapiens$/i }
)

let numberOfMice = db.materials.count(
  { 'scientific_name': /^Mus musculus$/i }
)

if (totalMaterials != (numberOfHumans + numberOfMice)) {
  throw 'The total number of records does not equal mice + men!'
}

// Update data
// Update mice
let result = db.materials.updateMany(
  { 'scientific_name': /^Mus musculus$/i },
  {
    $set: { taxon_id: "10090" }
  }
)

print(`${result.matchedCount} records matched`)
print(`${result.modifiedCount} records updated`)

// Update humans
result = db.materials.updateMany(
  { 'scientific_name': /^homo sapiens$/i },
  {
    $set: { taxon_id: "9606" }
  }
)

print(`${result.matchedCount} records matched`)
print(`${result.modifiedCount} records updated`)
