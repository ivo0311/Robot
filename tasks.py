from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a pdf file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=200)
    open_robot_order_website()
    download_orders_file()
    fill_form_with_csv_data()
    archive_receipts
    clean_up()

def open_robot_order_website():
    """Navigates to the given URL and clicks the pop up away."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')

def download_orders_file():
    """Downloads the CSV file with orders"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def order_another_robot():
    """Orders another robot"""
    page = browser.page()
    page.click("#order-another")

def clicks_ok():
    """Clicks OK"""
    page = browser.page()
    page.click('text=OK')

def fill_and_submit_robot_data(order):
    """Fills the form with robot data"""
    page = browser.page()
    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    head_number = order["Head"]
    page.select_option("#head", head_names.get(head_number))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(pdf_path, screenshot_path)
            order_another_robot()
            clicks_ok()
            break
    
def store_receipt_as_pdf(order_number):
    """Stores the receipt as a PDF file."""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def fill_form_with_csv_data():
    """Fills the form with the data from the CSV file"""
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        fill_and_submit_robot_data(order)

def screenshot_robot(order_number):
    """Saves the screenshot of the robot"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(pdf_path, screenshot_path):
    """Embeds the screenshot to the PDF receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path,
                                   source_path=pdf_path,
                                   output_path=pdf_path)
    
def archive_receipts():
    """Creates ZIP archive of the receipts and the images"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "output/receipts.zip")

def clean_up():
    """Cleans up the output folder"""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")