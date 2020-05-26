# Spam filtering with Vowpal Wabbit

This repository includes the backend code and a prototype frontend UI for performing active spam filter training using Vowpal Wabbit via a REST API.

## Setup

### Backend dependencies

CherryPy for the backend server, Scikit-learn for utility functions, Vowpal Wabbit for the actual model.

```
conda install cherrypy scikit-learn
```

```
pip install vowpalwabbit
```

### Frontend dependencies

Yarn to manage frontend dependencies, Node.js (https://nodejs.org/en/).

- Install Node.js (https://nodejs.org/en/)
- `npm install -g yarn`
- From the `frontend-ui-prototype` folder, `yarn build`  

