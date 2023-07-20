## An example project to explore the joining of SQLAlchemy and Strawberry GraphQL

The aim is to explore the possibilities of:
* Using the same model definition for both SQLAlchemy's ORM and the Strawberry GraphQL Schema
* Understand how to use GraphQL inputs consistently within the model
* How to implement pagination
* How to use efficient queries to avoid N+1 scenarios
* How to handle errors and their returns via GraphQL

### Model
This implements a very simple model.  There is a Dataset which can contain zero to many Datafiles.  
See the model/entity.py for details

### Running debug server
* Create the poetry environment using your favourite shell/IDE
* In the terminal run `poetry run python -m strawberrysqlalchemy.main` or run main.py from your IDE

### Example GraphQL Queries and Mutations
#### List all Datasets
```
{
  getDatasets {
    __typename
    ... on Datasets {
      datasets {
        id
        name
        retrievalUri
        datafiles {
          id
          filename
        }
      }
    }
    ... on DatasetError {
      title
      description
    }
  }
}
```

#### Add a Dataset
```
mutation {
  addDataset(datasetInput: {name: "dataset", retrievalUri: "uri"}) {
    __typename
    ... on Dataset {
      id
    }
    ... on DatasetError {
      title
      description
    }
  }
}
```

#### Add a Datafile to an existing Dataset
```
mutation {
  addDatafileToDataset(
    datasetId: 3
    datafileInput: {filename: "datafile 1.1", uri: "uri 1.1"}
  ) {
    __typename
    ... on Dataset {
      id
      datafiles {
        id
        datasetId
      }
    }
    ... on DatasetError {
      title
      description
    }
  }
}
```