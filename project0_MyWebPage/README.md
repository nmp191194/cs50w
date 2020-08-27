# Project 0

Web Programming with Python and JavaScript

In this project, I have created a simple HTML web page to introduce some things about myself, and to share some contents I enjoy.
On all pages, I include a Navbar component from Bootstrap library. The component contains 4 links to 4 pages of the project. In a large viewport, it is a full horizontal bar. When the viewport gets smaller, it is collapsed under 1 button.

 - index.html: About Me page
    + This page contains an image of myself
    + A list of Basic information
    + A table of Work Experience & Education
 - page1.html: Music I Like
    + 4 song cards, in a 2 by 2 grid with large viewport
    + The song cards fall into 1 column when viewport gets smaller
    + Colors, borders of the cards are configured in content_card.css (via SCSS)
 - page2.html: Artworks I Like
    + 2 artwork cards, in 1 column. Artwork is aligned to center
 - page3.html: Funny
    + 1 video card

The style for content cards like music-track, artwork & funny are constructed using the nested and inheritance syntax of SCSS. The colors are in hex code, so I used variable syntax of SCSS to give them names, making them more easily identifiable.

Dependencies:
   - Bootstrap (css & javascript)
   
