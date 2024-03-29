
@font-face {
    font-family: "et-book";
    src: url("_static/et-book/et-book-roman-line-figures/et-book-roman-line-figures.eot");
    src: url("_static/et-book/et-book-roman-line-figures/et-book-roman-line-figures.eot?#iefix") format("embedded-opentype"), url("et-book/et-book-roman-line-figures/et-book-roman-line-figures.woff") format("woff"), url("et-book/et-book-roman-line-figures/et-book-roman-line-figures.ttf") format("truetype"), url("et-book/et-book-roman-line-figures/et-book-roman-line-figures.svg#etbookromanosf") format("svg");
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}
             

@font-face {
    font-family: "et-book";
    src: url("_static/et-book/et-book-display-italic-old-style-figures/et-book-display-italic-old-style-figures.eot");
    src: url("_static/et-book/et-book-display-italic-old-style-figures/et-book-display-italic-old-style-figures.eot?#iefix") format("embedded-opentype"), url("et-book/et-book-display-italic-old-style-figures/et-book-display-italic-old-style-figures.woff") format("woff"), url("et-book/et-book-display-italic-old-style-figures/et-book-display-italic-old-style-figures.ttf") format("truetype"), url("et-book/et-book-display-italic-old-style-figures/et-book-display-italic-old-style-figures.svg#etbookromanosf") format("svg");
    font-weight: normal;
    font-style: italic;
    font-display: swap;
}

@font-face {
    font-family: "et-book";
    src: url("_static/et-book/et-book-bold-line-figures/et-book-bold-line-figures.eot");
    src: url("_static/et-book/et-book-bold-line-figures/et-book-bold-line-figures.eot?#iefix") format("embedded-opentype"), url("et-book/et-book-bold-line-figures/et-book-bold-line-figures.woff") format("woff"), url("et-book/et-book-bold-line-figures/et-book-bold-line-figures.ttf") format("truetype"), url("et-book/et-book-bold-line-figures/et-book-bold-line-figures.svg#etbookromanosf") format("svg");
    font-weight: bold;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: "et-book-roman-old-style";
    src: url("_static/et-book/et-book-roman-old-style-figures/et-book-roman-old-style-figures.eot");
    src: url("_static/et-book/et-book-roman-old-style-figures/et-book-roman-old-style-figures.eot?#iefix") format("embedded-opentype"), url("et-book/et-book-roman-old-style-figures/et-book-roman-old-style-figures.woff") format("woff"), url("et-book/et-book-roman-old-style-figures/et-book-roman-old-style-figures.ttf") format("truetype"), url("et-book/et-book-roman-old-style-figures/et-book-roman-old-style-figures.svg#etbookromanosf") format("svg");
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}



#search-input {
  font-family: "et-book", "Palatino", "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif;
  background-color: #fffff8;
}

* {
  font-family: "et-book", "Palatino", "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif;
  background-color: #fffff8;
  color: #111;
}

.footnote-reference brackets {
  font-family: "et-book", "Palatino", "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif;
  font-size: 0.75em;
}

.brackets {
  font-family: "et-book", "Palatino", "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif;
  font-size: 0.75em;
}


h1, h2, h3 {
    font-family: et-book, Palatino, "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif;
    text-align: left;
}

p {
    text-align: left;
    font-size: 1.25rem;
    line-height: 1.875rem;
}

body {
    margin-left: auto;
/*    font-family: et-book, Palatino, "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif; */
    background-color: #fffff8;
    color: #111;
    max-width: 1400px;
    text-align: left;
    counter-reset: sidenote-counter;
}

table, th, td, tr {
  border: 0em #fffff8;
  border-bottom: 0em #fffff8;
  border-style : hidden!important;
}

table  {
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 1em;
}


th, td {
  padding: .1em;
  border: 0em;
}

p.drop-cap {
  text-indent: 0em;
}
p.drop-cap:first-letter
{
  float: left;
  background-color: #111;
  color: #fffff8;
  margin: 0.15em 0.15em 0.15em 0.15em;
  font-size: 450%;
  line-height:0.85em;
}


.poem {
    padding-left: 2em;
    text-indent: -2em;
    margin-bottom: 0rem;
}
.poem-indent {
    padding-left: 2em;
    text-indent: -1em;
    margin-bottom: 0rem;
}

.poem-big-indent {
    padding-left: 3em;
    margin-bottom: 0rem;
}
.poem-bigger-indent {
    padding-left: 4em;
    margin-bottom: 0rem;
}
.poem-biggest-indent {
    padding-left: 5em;
    margin-bottom: 0rem;
}

.dot-table td {
  padding-left: 2em;
}


.dot-table td {
  max-width:200px;
  overflow:hidden;
  white-space:nowrap;
}

.dot-table3 th:nth-child(1) {
  padding-right: 2em;
  text-align: right;
}

.dot-table3 th {
  text-align: right;
}

.dot-table td:nth-child(2) {
  text-align: right;
  padding-right: 2em;
}

.dot-table td:first-child:after {
  content:" . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . "
}

.dot-table3 td:nth-child(3):after {
  content:" . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . "
}

.dot-table3 td:nth-child(4) {
  text-align: right;
}
.col-table td  {
  vertical-align: top;
}

@media print {
  background-color: #FFFFFF;
  width: 55%;
}