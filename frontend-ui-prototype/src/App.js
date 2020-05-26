import { Container } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import blue from "@material-ui/core/colors/blue";
import teal from "@material-ui/core/colors/teal";
import { createMuiTheme, MuiThemeProvider } from "@material-ui/core/styles";
import React from "react";
import { useDispatch } from "react-redux";
import DraggableDialog from "./ClassificationReportDialog";
import EmailGrid from "./EmailGrid";
import useStyles from "./material-styles";
import { getEmail, getRandomEmails, showReport } from "./spamFilterSlice";

const theme = createMuiTheme({
  palette: {
    primary: blue,
    secondary: teal,
  },
  typography: {
    fontSize: 14,
  },
});

function App() {
  const classes = useStyles();
  const dispatch = useDispatch();

  return (
    <MuiThemeProvider theme={theme}>
      <Container maxWidth="lg" className={classes.topSpace}>
        <EmailGrid />
        <DraggableDialog />
        <Button
          variant="contained"
          className={classes.simpleSpacer}
          color={"primary"}
          onClick={() => dispatch(showReport())}
        >
          Show classification report
        </Button>
        <Button
          variant="contained"
          className={classes.simpleSpacer}
          color={"secondary"}
          onClick={() => dispatch(getRandomEmails())}
        >
          Load 10 new emails
        </Button>
        <Button
          variant="contained"
          className={classes.simpleSpacer}
          onClick={() => {
            dispatch(getEmail("11399"));
          }}
        >
          Debug: Fetch email 11399
        </Button>
      </Container>
    </MuiThemeProvider>
  );
}

export default App;
