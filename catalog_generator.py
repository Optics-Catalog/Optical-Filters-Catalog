import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import qrcode
from PIL import Image, ImageDraw, ImageFont


RAW_FOLDER = "raw_data"
REPORT_FOLDER = "reports"
QR_FOLDER = "qr_codes"
RAW_EXPORT_FOLDER = "raw_exports"


# Change after hosting
PUBLIC_URL = (
    "http://10.53.66.192:8000/reports/"
)


for folder in [
    REPORT_FOLDER,
    QR_FOLDER,
    RAW_EXPORT_FOLDER
]:
    os.makedirs(folder, exist_ok=True)



# -----------------------------------------
# Read spectrometer raw file
# -----------------------------------------

def read_spectrum_file(filename):

    metadata = {}

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        lines = f.readlines()


    data_start = None


    for i,line in enumerate(lines):

        if line.startswith("Pixel;"):
            data_start=i
            break


        if ";" in line:

            key,value=line.strip().split(
                ";",
                1
            )

            metadata[key.strip()] = value.strip()



    data=pd.read_csv(
        filename,
        sep=";",
        skiprows=data_start
    )


    return metadata,data



# -----------------------------------------
# Create interactive graphs
# -----------------------------------------

def create_graphs(data):

    spectrum = go.Figure()

    spectrum.add_trace(
        go.Scatter(
            x=data["Wavelength"],
            y=data["Dark Subtracted #1"],
            mode="lines",
            name="spectrum"
        )
    )

    spectrum.update_xaxes(range=[300, data["Wavelength"].max()])

    spectrum.update_layout(
        title="Spectrum",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Intensity",
        template="plotly_white", 
    )

    spectrum.update_layout(
    autosize=True,
    margin=dict(l=30, r=30, t=40, b=40)
    )

    spectrum_html=pio.to_html(
        spectrum,
        full_html=False,
        include_plotlyjs="cdn",
        config={"responsive": True}
    )



    tr=go.Figure()


    tr.add_trace(
        go.Scatter(
            x=data["Wavelength"],
            y=data["%TR #1"],
            mode="lines",
            name="%T/R"
        )
    )

    tr.update_xaxes(range=[300, data["Wavelength"].max()])

    tr.update_layout(
        title="%T/R Spectrum",
        xaxis_title="Wavelength (nm)",
        yaxis_title="%T/R",
        template="plotly_white",
    )
    tr.update_layout(
        autosize=True,
        margin=dict(l=30, r=30, t=40, b=40)
    )


    tr_html=pio.to_html(
        tr,
        full_html=False,
        include_plotlyjs=False,
        config = {"responsive" :True}
    )


    return spectrum_html,tr_html

# -----------------------------------------
# Create Index
# -----------------------------------------
def create_index():
    rows = ""

    for _, row in filters.iterrows():

        fid = str(row["filter_id"]).strip()

        rows += f"""
    <tr>

    <td>{fid}</td>

    <td>{row.get("catalog_number","")}</td>

    <td>{row.get("description","")}</td>

    <td>{row.get("supplier","")}</td>

    <td>{row.get("filter_type","")}</td>

    <td>{row.get("center_nm","")}</td>

    <td>

    <a class="button"
    href="{fid}.html">

    Open Report

    </a>

    </td>

    <td>

    <a class="button"
    href="../raw_exports/{fid}_raw.csv">

    CSV

    </a>

    </td>

    </tr>
    """
    # -----------------------------------------
    # Create HTML page for report directory
    # -----------------------------------------

    html = f"""

    <!DOCTYPE html>

    <html>

    <head>

    <meta charset="utf-8">

    <meta name="viewport"
    content="width=device-width, initial-scale=1">

    <title>Filter Catalog</title>

    <link rel="stylesheet"
    href="https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css">

    <style>

    body{{

    font-family:Arial;
    background:#f5f5f5;
    margin:20px;

    }}

    h1{{

    color:#174873;

    }}

    .button{{

    background:#174873;
    color:white;

    padding:8px 14px;

    border-radius:6px;

    text-decoration:none;

    }}

    .button:hover{{

    background:#25639b;

    }}

    table.dataTable tbody tr:hover{{

    background:#eef7ff;

    }}

    @media(max-width:700px){{

    body{{
    margin:10px;
    }}

    }}

    </style>

    </head>

    <body>

    <h1>Optical Filter Catalog</h1>

    <table id="filters"
    class="display">

    <thead>

    <tr>

    <th>Filter ID</th>

    <th>Catalog</th>

    <th>Description</th>

    <th>Supplier</th>

    <th>Type</th>

    <th>Center (nm)</th>

    <th>Report</th>

    <th>CSV</th>

    </tr>

    </thead>

    <tbody>

    {rows}

    </tbody>

    </table>

    <script
    src="https://code.jquery.com/jquery-3.7.1.min.js">
    </script>

    <script
    src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js">
    </script>

    <script>

    $(document).ready(function(){{

    $('#filters').DataTable({{

    pageLength:25,

    responsive:true,

    order:[[0,"asc"]],

    language:{{
    search:"Search:"
    }}

    }});

    }});

    </script>

    </body>

    </html>

    """   

    filename = os.path.join(
        REPORT_FOLDER,
        "index.html"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)


# -----------------------------------------
# Create HTML page for reports
# -----------------------------------------

def create_html(
        filter_info,
        metadata,
        data
):


    filter_id = str(filter_info["filter_id"]).strip()


    dark_graph,tr_graph=create_graphs(
        data
    )


    # export raw data
    raw_export=os.path.join(
        RAW_EXPORT_FOLDER,
        filter_id + "_raw.csv"
    )

    data.to_csv(
        raw_export,
        index=False
    )


    general_specs = ""
    optical_specs = ""
    measurement_specs = ""


    # xslx information

    general_fields = [
        "catalog_number",
        "filter_id",
        "description",
        "supplier"
    ]

    for field in general_fields:

        value = filter_info.get(field, "")

        general_specs += f"""
        <div class="spec-row">
            <div class="spec-label">{field.title()}</div>
            <div class="spec-value">{value}</div>
        </div>
        """

    optical_fields = [
    "filter_type",
    "application",
    "cut_on_nm",
    "cut_off_nm",
    "center_nm",
    "bandwidth_nm"
]

    for field in optical_fields:

        value = filter_info.get(field, "")

        if pd.isna(value):
            value = "—"

        elif field.endswith("_nm") and value != "":
            value = f"{float(value):.2f} nm"

        optical_specs += f"""
        <div class="spec-row">
            <div class="spec-label">{field.title()}</div>
            <div class="spec-value">{value}</div>
        </div>
        """

    important_metadata = [
    "Date",
    "model",
    "title",
    "operator",
    "intigration times",
    "average number",
    "spectrometer_type"
]

    for key in important_metadata:

        if key not in metadata:
            continue

        value = metadata[key]

        try:
            value = f"{float(value):.2f}"
        except (ValueError, TypeError):
            pass

        measurement_specs += f"""
        <div class="spec-row">
            <div class="spec-label">{key.title()}</div>
            <div class="spec-value">{value}</div>
        </div>
        """

    html=f"""

<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">


<title>
Filter {filter_id}
</title>


<style>

body {{
font-family:Arial;
background:#f5f5f5;
margin:15px;
}}


.card {{

background:white;
padding:20px;
border-radius:15px;
margin-bottom:20px;
box-shadow:0px 3px 8px #bbb;

}}

.specifications {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.spec-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
    padding: 10px;
    border-bottom: 1px solid #ddd;
}}

.spec-label {{
    font-weight: bold;
    color: #174873;
    flex: 1;
}}

.spec-value {{
    flex: 2;
    text-align: right;
    overflow-wrap: anywhere;
    word-break: break-word;
}}

h1 {{

color:#174873;

}}

.button {{

background:#174873;
color:white;
padding:12px;
border-radius:8px;
text-decoration:none;

}}

@media (max-width: 700px) {{

    .spec-row {{
        flex-direction: column;
        gap: 4px;
    }}

    .spec-label {{
        font-size: 15px;
    }}

    .spec-value {{
        text-align: left;
        font-size: 14px;
    }}

}}

</style>


</head>



<body>


<h1>
Filter {filter_id}
</h1>


<div class="card">
<h2>General Information</h2>

<div class="specifications">
{general_specs}
</div>

</div>

<div class="card">
<h2>Optical Specifications</h2>

<div class="specifications">
{optical_specs}
</div>

</div>

<div class="card">
<h2>Measurement Information</h2>

<div class="specifications">
{measurement_specs}
</div>

</div>



<div class="card">

{dark_graph}

</div>



<div class="card">

{tr_graph}

</div>



<div class="card">

<a class="button"
href="../raw_exports/{filter_id}_raw.csv">

Download raw data

</a>

</div>



</body>

</html>

"""

    filename=os.path.join(
        REPORT_FOLDER,
        filter_id+".html"
    )


    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

# -----------------------------------------
# Create QR code
# -----------------------------------------

def create_qr(filter_id, catalog_number):

    url = PUBLIC_URL + filter_id + ".html"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    # Font
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(qr_img)

    # Measure text
    bbox = draw.textbbox((0, 0), catalog_number, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    margin = 10

    # Create a taller image
    final_img = Image.new(
        "RGB",
        (
            qr_img.width,
            qr_img.height + text_height + margin * 2
        ),
        "white"
    )

    final_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final_img)

    x = (qr_img.width - text_width) // 2
    y = qr_img.height + margin

    draw.text(
        (x, y),
        catalog_number,
        fill="black",
        font=font
    )

    final_img.save(
        os.path.join(
            QR_FOLDER,
            filter_id + ".png"
        )
    )



# -----------------------------------------
# MAIN
# -----------------------------------------


filters = pd.read_excel("filters.xlsx", dtype=str)

filters["report_path"] = ("reports/"+filters["filter_id"].str.strip()+".html")

# -----------------------------------------
# MAIN
# -----------------------------------------

title = "OPTICAL FILTER CATALOG GENERATOR"

print("=" * 60)
print("=" + " " * 58 + "=")
print("=" + title.center(58) + "=")
print("=" + " " * 58 + "=")
print("=" * 60)

print()

print("Initializing...\n")

for _, filter_info in filters.iterrows():

    filter_id = str(filter_info["filter_id"]).strip()


    print(
        "Generating",
        filter_id
    )


    raw_file = os.path.join(
        RAW_FOLDER,
        str(filter_info["raw_file"]).strip()
    )

    metadata,data=read_spectrum_file(
        raw_file
    )


    create_html(
        filter_info,
        metadata,
        data
    )


    create_qr(
        filter_id,
        str(filter_info["catalog_number"])
    )

    create_index()

filters.to_excel("filters_with_links.xlsx", index=False)

print(
    "\nCATALOG READY"
)