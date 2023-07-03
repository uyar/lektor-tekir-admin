# Copyright (C) 2023 H. Turgut Uyar <uyar@tekir.org>
#
# lektor-tekir is released under the BSD license.
# Read the included LICENSE.txt file for details.

from pathlib import Path

from flask import Blueprint, g, render_template, request
from flask_babel import gettext as _


MULTILINE = {"text", "strings", "markdown", "html", "rst", "flow"}


bp = Blueprint("admin_tekir_api", __name__, url_prefix="/admin-tekir/api")


@bp.route("/page-count")
def page_count():
    root_path = Path(g.admin_context.pad.env.root_path)
    pages = {c.parent for c in root_path.glob("**/contents*.lr")}
    return str(len(pages))


@bp.route("/subpages")
def subpages():
    g.lang_code = request.args.get("lang", "en")
    path = request.args.get("path")
    node = g.admin_context.tree.get(path)
    children = [c._primary_record for c in node.iter_subpages()]
    return render_template("tekir_subpages.html",
                           current=node._primary_record, records=children)


@bp.route("/attachments")
def attachments():
    g.lang_code = request.args.get("lang", "en")
    path = request.args.get("path")
    node = g.admin_context.tree.get(path)
    children = [c._primary_record for c in node.iter_attachments()]
    return render_template("tekir_attachments.html",
                           current=node._primary_record, records=children)


def field_entry(field, field_name=None):
    if field_name is None:
        field_name = field.name
    value = request.form.get(field_name)
    if field.type.name == "boolean":
        value = "yes" if value == "on" else "no"
        if field.default in {"true", "yes", "1"}:
            default = "yes"
        elif field.default in {"false", "no", "0"}:
            default = "no"
        if value == default:
            value = None
    if value is not None:
        value = value.strip()
    if not value:
        return None
    if field.type.name in MULTILINE:
        stripped = "\n".join(line.strip() for line in value.splitlines())
        return f"{field.name}:\n\n{stripped}"
    else:
        return f"{field.name}: {value}"


def flowblock_entry(node, field):
    block_data = [k for k in request.form if k.startswith(f"{field.name}-")]
    if len(block_data) == 0:
        return None
    n_blocks = max(int(k.split("-")[1]) for k in block_data)
    entries = []
    for i in range(1, n_blocks + 1):
        prefix = f"{field.name}-{i}-"
        block_fields = [k for k in request.form if k.startswith(prefix)]
        block_types = {f.split("-")[2] for f in block_fields}
        if len(block_types) > 1:
            raise RuntimeError("All fields must be of the same flowblock type")
        block_type_id = block_fields[0].split("-")[2]
        block_header = f"#### {block_type_id} ####"
        block_type = node.tree.pad.db.flowblocks[block_type_id]
        block_entries = []
        for block_field in block_type.fields:
            field_name = f"{field.name}-{i}-{block_type_id}-{block_field.name}"
            block_entry = field_entry(block_field, field_name)
            if not block_entry:
                continue
            block_entries.append(block_entry)
        entries.append(block_header + "\n" + "\n----\n".join(block_entries))
    return f"{field.name}:\n\n" + "\n".join(entries)


@bp.route("/save_content", methods=["POST"])
def save_content():
    g.lang_code = request.args.get("lang", "en")
    path = request.args.get("path")
    node = g.admin_context.tree.get(path)
    record = node._primary_record
    entries = []

    try:
        default_model = record.parent.datamodel.child_config.model
    except AttributeError:
        default_model = None
    if default_model is None:
        default_model = "page"
    if record["_model"] != default_model:
        entries.append(f"_model: {record['_model']}")

    if record["_template"] != record.datamodel.get_default_template_name():
        entries.append(f"_template: {record['_template']}")

    for field in record.datamodel.fields:
        if field.type.name == "flow":
            entry = flowblock_entry(node, field)
        else:
            entry = field_entry(field)
        if not entry:
            continue
        entries.append(entry)

    content = "\n---\n".join(entries) + "\n"
    source = Path(record.source_filename)
    old_content = source.read_text()
    if content != old_content:
        source.write_text(content)
    return _("Content saved.")
