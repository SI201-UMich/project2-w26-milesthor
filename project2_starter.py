# SI 201 HW4 (Library Checkout System)
# Your name: Miles Thornton
# Your student id: 4762 4083
# Your email: milethor@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    with open(html_path, "r", encoding= "utf-8-sig") as file:

        results = []

        seen = []

        content = file.read()
        soup = BeautifulSoup(content, "html.parser")

        listing_tags = soup.find_all("a", href=re.compile(r"/rooms(?:/plus)?/\d+"))

        for tag in listing_tags:

            href = tag.get("href")

            matched_code = re.search(r"/rooms(?:/plus)?/(\d+)",href)

            if not matched_code:

                continue

            listing_id = matched_code.group(1)

            if listing_id in seen:
                continue
            seen.append(listing_id)

            container = tag.parent.parent.parent.parent
            title_div = container.find("div", class_=re.compile(r"t1jojoys"))
            
            if title_div:
                listing_title = title_div.get_text(strip=True)
            else:
                listing_title = ""

            results.append((listing_title,listing_id))
        
        return results

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(file_path, "r", encoding="utf-8-sig") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    
    #Policy Number
    policy_number = "Pending"

    policy_tag = soup.find(string=re.compile(r"Policy number:", re.IGNORECASE))
    
    if policy_tag:
        li_tag = policy_tag.parent
        span = li_tag.find("span")

        if span:
            raw_text = span.get_text(strip=True)
            if re.search(r"pending", raw_text, re.IGNORECASE):
                policy_number = "Pending"
            elif re.search(r"exempt", raw_text, re.IGNORECASE):
                policy_number = "Exempt"
            else:
                policy_number = raw_text
    
    #Host Type
    superhost_tag = soup.find(string=re.compile(r"Superhost"))
    if superhost_tag:
        host_type = "Superhost"
    else:
        host_type = "Regular"
    
    #Host name and room type
    host_name = ""
    room_type = "Entire Room"

    subtitle_tag = soup.find("h2", class_="_14i3z6h")

    if subtitle_tag:
        subtitle_text = subtitle_tag.get_text(strip=True)
    
        if "hosted by" in subtitle_text.lower():
            host_name = subtitle_text.split("hosted by")[-1].strip()

            host_name = host_name.replace("\xa0", "").strip()
        
        if "Private" in subtitle_text:
            room_type = "Private Room"
        elif "Shared" in subtitle_text:
            room_type = "Shared Room"
        else:
            room_type = "Entire Room"
    
    #Location Rating

    location_rating = 0.0

    location_tags = soup.find_all("div", class_="_y1ba89")
    for tag in location_tags:
        if tag.get_text(strip=True) == "Location":
            grandparent_text = tag.parent.get_text(strip=True)
            rating_match = re.search(r"(\d+\.\d+)", grandparent_text)
            if rating_match:
                location_rating = float(rating_match.group(1))
            break
    return {
        listing_id: {
            "policy_number" : policy_number,
            "host_type" : host_type,
            "host_name" : host_name,
            "room_type" : room_type,
            "location_rating" : location_rating
        }
    }

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    listings = load_listing_results(html_path)

    results = []

    for listing_title, listing_id in listings:

        details = get_listing_details(listing_id)

        inner = details[listing_id]

        result_tuple = (

            listing_title,
            listing_id,
            inner["policy_number"],
            inner["host_type"],
            inner["host_name"],
            inner["room_type"],
            inner["location_rating"]
        )

        results.append(result_tuple)
    
    return results

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True)

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:

        writer = csv.writer(file)

        writer.writerow([

            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name",
            "Room Type",
            "Location Rating"

        ])

        for row in sorted_data:

            writer.writerow(row)

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    




    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.

        self.assertEqual(len(self.listings), 18)

        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        results = []
        for listing_id in html_list:
            results.append(get_listing_details(listing_id))

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349"
        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")


        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)
        

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        output_csv(self.detailed_data, out_path)

        # TODO: Read the CSV back in and store rows in a list.
        rows = []
        with open(out_path, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)

        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])


        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)