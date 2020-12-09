What Bookkeeper does:
    Bookkeeper is a web application that keeps tracks of a users reading habbits and the books they have read.
    It was inspired by an Excel sheet that I currently use to keep track of my reading. Bookeeper is meant to
    be used by a person for their own personal interest and organization. Some of the functionality of Bookeeper
    includes:
        - Registration and Logging in as a user
        - Adding a book to a "To-Read" list
        - Marking a book as completed and giving a review
        - Viewing lists of To-Read books
        - Viewing lists of Books Read
        - Filtering both of these lists by categories such as name, date and score
        - Keeps a running total of different statistics such as average score, total books and total pages read

How Bookkeeper works:

    Front end:
        Bookkeeper uses html and css for the styling of it's web pages. It relies much less heavily on bootstrap compared to
        other projects and strives to look a bit less like most websites. It does look less like the "average" website
        but the tradeoff is that it looks less proffessional than a website with more bootstrap elements.

    Framework/mid-layer:
        Bookkeeper uses the tech stack that we were taught near the end of CS50 for all of it's operations. It relies
        on Python for all of the logic and most of the checks associated with different functions. Along with Python
        it uses the Flask framework for the setup and for navigating between pages. A different Python function is used
        for each of the different filters that can be applied to the list of books read and to-read.

    Backend:
        Bookkeeper relies on an SQL database with 3 main tables for it's record keeping. An SQL script is provided for refreshing
        the database to a blank state if required. The data is seperated into 3 tables for books, users and reviews.
