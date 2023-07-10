window.addEventListener("DOMContentLoaded", (loadEvent) => {

    /* confirming deletes */

    const deleteDialog = document.getElementById("delete-confirm");

    document.querySelectorAll(".delete-content").forEach((el) => {
        el.addEventListener("click", (ev) => {
            document.getElementById("delete-continue").setAttribute("hx-include", "#" + el.closest("form").id);
            deleteDialog.showModal();
        });
    });

    document.querySelectorAll("#delete-continue").forEach((el) => {
        el.addEventListener("click", (ev) => {
            ev.preventDefault();
            const formId = el.getAttribute("hx-include");
            document.querySelector(formId).querySelectorAll("input:checked").forEach((checkbox) => {
                checkbox.closest("tr").remove();
            });
            deleteDialog.close();
        });
    });

    document.querySelectorAll("#delete-cancel").forEach((el) => {
        el.addEventListener("click", (ev) => {
            ev.preventDefault();
            deleteDialog.close();
        });
    });

    /* saving content and checking for unsaved changes */

    const saveDialog = document.getElementById("save-dialog");

    document.querySelectorAll("#save-content").forEach((el) => {
        el.addEventListener("click", (ev) => {
            saveDialog.showModal();
        });
    });

    document.querySelectorAll("#save-close").forEach((el) => {
        el.addEventListener("click", (ev) => {
            saveDialog.close();
        });
    });

    const changesDialog = document.getElementById("changes-dialog");

    document.querySelectorAll("#check-changes").forEach((el) => {
        el.addEventListener("click", (ev) => {
            changesDialog.showModal();
        });
    });

    document.querySelectorAll("#changes-continue").forEach((el) => {
        el.addEventListener("click", (ev) => {
            changesDialog.close();
            // window.location.href = "{{ url_for('tekir_admin.contents', path=record.path) }}";
        })
    });

    document.querySelectorAll("#changes-cancel").forEach((el) => {
        el.addEventListener("click", () => {
            changesDialog.close();
        });
    });

    /* deleting and ordering flow blocks */

    document.querySelectorAll(".delete-block").forEach((el) => {
        el.addEventListener("click", (ev) => {
            ev.preventDefault();
            details = el.closest("details");
            if (details.querySelectorAll(".up-block").length == 0) {
                summary = el.closest("summary");
                downSummary = details.nextElementSibling.querySelector("summary");
                downSummary.after(summary);
                downSummary.remove();
            }
            details.remove();
        });
    });

    document.querySelectorAll(".up-block").forEach((el) => {
        el.addEventListener("click", (ev) => {
            ev.preventDefault();
            details = el.closest("details");
            fieldset = details.querySelector("fieldset");
            upDetails = details.previousElementSibling;
            upFieldset = upDetails.querySelector("fieldset");
            details.append(upFieldset);
            upDetails.append(fieldset);
        });
    });
});
