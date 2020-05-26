import CssBaseline from "@material-ui/core/CssBaseline";
import { configureStore } from "@reduxjs/toolkit";
import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import "typeface-roboto";
import App from "./App";
import spamFilterReducer, { getRandomEmails } from "./spamFilterSlice";

const store = configureStore({
  reducer: spamFilterReducer,
});

// Actions to dispatch globally before components load
store.dispatch(getRandomEmails());

ReactDOM.render(
  <Provider store={store}>
    <CssBaseline />
    <App />
  </Provider>,
  document.getElementById("root")
);
