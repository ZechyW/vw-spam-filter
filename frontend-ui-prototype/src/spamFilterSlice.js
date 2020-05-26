import { createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import { forOwn, keys } from "lodash";
import { API_HOST } from "./conf";

const spamFilterSlice = createSlice({
  name: "spamFilter",
  initialState: {
    emails: {},
    reportOpen: false,
    reportDetails: {
      count_ham: -1,
      count_spam: -1,
      report: "",
    },
  },
  reducers: {
    loadEmails(state, action) {
      // Given a list of (random) emails from the server, load them into `state.emails`
      const emails = {};
      for (let email of action.payload) {
        emails[email.id] = email;
      }
      state.emails = emails;
    },
    loadEmail(state, action) {
      // Load/Update the details for one particular email into the local state cache
      const email = action.payload;
      state.emails[email.id] = email;
    },
    openReportDialog(state) {
      state.reportOpen = true;
    },
    closeReportDialog(state) {
      state.reportOpen = false;
    },
    loadReportDetails(state, action) {
      state.reportDetails = action.payload;
    },
  },
});

export const {
  loadEmails,
  loadEmail,
  openReportDialog,
  closeReportDialog,
  loadReportDetails,
} = spamFilterSlice.actions;

export default spamFilterSlice.reducer;

// Thunks
export const getRandomEmails = () => async (dispatch) => {
  // Load a randomised email set into the redux store
  try {
    const response = await axios.get(`${API_HOST}/email`);
    dispatch(loadEmails(response.data));
  } catch (err) {
    console.log(err.toString());
  }
};

export const getEmail = (email_id) => async (dispatch) => {
  // Load/Update the email with the given ID into the redux store
  try {
    const response = await axios.get(`${API_HOST}/email/${email_id}`);
    dispatch(loadEmail(response.data));
  } catch (err) {
    console.log(err.toString());
  }
};

export const setLabel = (email_id, label) => async (dispatch) => {
  try {
    await axios.put(`${API_HOST}/email/${email_id}/label`, {
      label,
    });
    dispatch(updateAllEmails());
  } catch (err) {
    console.log(err.toString());
  }
};

export const updateAllEmails = () => async (dispatch, getState) => {
  const { emails } = getState();
  forOwn(keys(emails), (email_id) => {
    dispatch(getEmail(email_id));
  });
};

export const showReport = () => async (dispatch) => {
  try {
    const response = await axios.get(`${API_HOST}/report`);
    dispatch(loadReportDetails(response.data));
    dispatch(openReportDialog());
  } catch (err) {
    console.log(err.toString());
  }
};
