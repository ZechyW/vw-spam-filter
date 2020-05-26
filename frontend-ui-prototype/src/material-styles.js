import { makeStyles } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  topSpace: {
    marginTop: theme.spacing(6),
  },
  detailView: {
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    maxHeight: "300px",
    overflowY: "scroll",
    backgroundColor: theme.palette.grey["50"],
  },
  wordOverflow: {
    // For extra-long content lines that otherwise cause the table to stretch beyond the root container
    overflowWrap: "break-word",
    maxWidth: "1000px",
  },
  simpleSpacer: {
    margin: theme.spacing(2),
  },
}));

export default useStyles;
