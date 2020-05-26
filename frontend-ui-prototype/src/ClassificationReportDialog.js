import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import Paper from "@material-ui/core/Paper";
import React from "react";
import Draggable from "react-draggable";
import { useDispatch, useSelector } from "react-redux";
import { closeReportDialog } from "./spamFilterSlice";

function PaperComponent(props) {
  return (
    <Draggable
      handle="#draggable-dialog-title"
      cancel={'[class*="MuiDialogContent-root"]'}
    >
      <Paper {...props} />
    </Draggable>
  );
}

export default function DraggableDialog() {
  const dispatch = useDispatch();

  const open = useSelector((state) => state.reportOpen);
  const reportDetails = useSelector((state) => state.reportDetails);

  return (
    <div>
      <Dialog
        open={open}
        onClose={() => dispatch(closeReportDialog())}
        PaperComponent={PaperComponent}
        aria-labelledby="draggable-dialog-title"
      >
        <DialogTitle style={{ cursor: "move" }} id="draggable-dialog-title">
          Classification Report
        </DialogTitle>
        <DialogContent>
          <DialogContentText component={"div"}>
            <div>
              User has provided <b>{reportDetails.count_ham} ham</b> and{" "}
              <b>{reportDetails.count_spam} spam</b> labels for the current
              model.
            </div>
            <div>The model performs as follows on the test set:</div>
            <pre>{reportDetails.report}</pre>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => dispatch(closeReportDialog())} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
