const neo4j = require('neo4j-driver');
const driver = neo4j.driver(
  'bolt://localhost:7687',
  neo4j.auth.basic('neo4j', 'password123')
);

const session = driver.session();

async function createNodes() {
  await session.run(`
    CREATE (jehan:Person {name: "Jehan Rodrigo", email: "jehanrodrigo31@gmail.com"})
  `);
  console.log("Nodes created!");
  await session.close();
  await driver.close();
}

createNodes();