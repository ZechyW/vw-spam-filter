import { Typography } from "@material-ui/core";
import { cloneDeep, forOwn } from "lodash";
import MaterialTable from "material-table";
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import tableIcons from "./material-icons";
import useStyles from "./material-styles";
import { setLabel } from "./spamFilterSlice";

function EmailGrid() {
  const classes = useStyles();
  const dispatch = useDispatch();

  // Transform email data for display
  const emails = useSelector((state) => state.emails);
  let tableData = [];
  forOwn(cloneDeep(emails), (email) => {
    email.content = email.content.trim();
    email.prediction = (parseFloat(email.prediction) * 100).toFixed(2);
    tableData.push(email);
  });
  tableData = tableData.sort((a, b) => parseInt(a.id) - parseInt(b.id));

  return (
    <MaterialTable
      icons={tableIcons}
      columns={[
        {
          title: "ID",
          field: "id",
          width: "50px",
        },
        { title: "Subject", field: "subject" },
        {
          title: "Ham Probability",
          field: "prediction",
          width: "110px",
          render: (rowData) =>
            rowData.prediction > 50 ? (
              <Typography variant={"body2"} color={"primary"}>
                <b>{`${rowData.prediction}%`}</b>
              </Typography>
            ) : (
              <Typography variant={"body2"} color={"textSecondary"}>
                {`${rowData.prediction}%`}
              </Typography>
            ),
          customSort: (a, b) => a.prediction - b.prediction,
        },
      ]}
      data={tableData}
      title="Spam Filter Demo"
      detailPanel={(rowData) => {
        // Remove extraneous newlines, prepare to display using <br/>s
        // (React doesn't let us render strings as HTML directly by default)
        const textLines = rowData.content
          .replace(/(\s*\r?\n\r?){4,}/g, "\n\n\n")
          .split(/\r?\n\r?/);
        return (
          <div className={classes.detailView}>
            <Typography variant={"body2"} component={"div"}>
              {textLines.map((line, index) => (
                <div className={classes.wordOverflow} key={index}>
                  {line}
                  <br />
                </div>
              ))}
            </Typography>
          </div>
        );
      }}
      onRowClick={(event, rowData, togglePanel) => togglePanel()}
      options={{
        actionsCellStyle: {
          width: "130px",
          textAlign: "center",
        },
        actionsColumnIndex: -1,
        rowStyle: {},
        pageSize: 10,
      }}
      actions={[
        (rowData) => ({
          icon: rowData.label === "1" ? tableIcons.HamSet : tableIcons.HamUnset,
          tooltip: rowData.label === "1" ? "Marked as Ham" : "Mark as Ham",
          onClick: (event, rowData) => {
            if (rowData.label !== "1") {
              dispatch(setLabel(rowData.id, "ham"));
            }
          },
        }),
        (rowData) => ({
          icon:
            rowData.label === "-1" ? tableIcons.SpamSet : tableIcons.SpamUnset,
          tooltip: rowData.label === "-1" ? "Marked as Spam" : "Mark as Spam",
          onClick: (event, rowData) => {
            if (rowData.label !== "-1") {
              dispatch(setLabel(rowData.id, "spam"));
            }
          },
        }),
      ]}
      localization={{
        header: {
          actions: "Ham / Spam",
        },
      }}
    />
  );
}

export default EmailGrid;
