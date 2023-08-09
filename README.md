# GPT-Paper

Enhance paper search, reading, writing and review with the assistance of GPT.

## Data pre-processing

### How to categorize headers and footers?

One practical method is to use clustering algorithms (such as **DBSCAN**) based on some metrics (such as the **coordinates** of the bound points for the block rectangle, and the **length** of the block text, in short: `(x0,y0,x1,y1,len(text))`).

![](./examples/headers-categorize-1.png)

See my answer here:

* Is there a way to delete headers/footers in PDF documents? · pymupdf/PyMuPDF · Discussion #2259
  * https://github.com/pymupdf/PyMuPDF/discussions/2259#discussioncomment-6669190