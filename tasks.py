from robocorp import browser
from robocorp.tasks import task
from RPA.Archive import Archive
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        preview_robot()
        sucess = False
        while not sucess:
            submit_order()
            sucess = check_alert()
        pdf_filepath = store_receipt_as_pdf(order)
        screenshot_filepath = screenshot_robot(order)
        embed_screenshot_to_receipt(screenshot_filepath, pdf_filepath)
        # break # remove
        order_next()
    archive_receipts()


def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv("orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    page = browser.page()

    page.select_option("#head", str(order["Head"]))
    page.query_selector_all("input[type=radio]")[int(order["Body"])-1].click()
    # radios = page.query_selector(f"input[type='radio'][id=id-body-{order['Body']}]").click() #another way
    page.fill("input[type='number'][placeholder='Enter the part number for the legs']", order["Legs"])            
    page.fill("#address", str(order["Address"]))
    
def preview_robot():
    page = browser.page()
    page.click("button:text('Preview')") 

def submit_order():
    page = browser.page()
    page.click("button:text('ORDER')")

def check_alert():
    page = browser.page()   
    return False if page.query_selector("div[class='alert alert-danger']") else True

def store_receipt_as_pdf(order):
    page = browser.page()
    order_recept_html = page.locator("div[class='alert alert-success']").inner_html()
    pdf = PDF()
    path = f"output/receipts/order_receipt_order_{order['Order number']}.pdf"
    pdf.html_to_pdf(order_recept_html, path)
    return path

def screenshot_robot(order):
    page = browser.page()
    robot_review = page.locator("#robot-preview-image")
    path = f"output/screenshots/robot_preview_order_{order['Order number']}.png"
    robot_review.screenshot(path=path)    
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[pdf_file, screenshot],
        target_document=pdf_file
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output/receipts', 'output/receipts.zip')

def order_next():
    page = browser.page()
    page.click("button:text('Order another robot')")