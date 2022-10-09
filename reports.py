import re
from turtle import title
import numpy as np
from reportlab.lib.pagesizes import A4,letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, 
    Frame, 
    PageTemplate, 
    NextPageTemplate, 
    Paragraph, 
    PageBreak, 
    ListFlowable,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)

class NumberedCanvas(canvas.Canvas):
    '''Inspired by https://stackoverflow.com/q/59429543'''
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont('Helvetica', 9)
        self.setLineWidth(0.1)
        self.setStrokeColor(colors.black, alpha=0.2)
        self.setFillColor(colors.black, alpha=0.4)
        self.line(cm, 1.5 * cm, self._pagesize[0] - cm, 1.5 * cm)
        self.drawRightString(
            self._pagesize[0] - cm, 1.1 * cm, 
            "Page %d of %d" % (self._pageNumber, page_count)
        )

class AnalyticsReport(BaseDocTemplate):
    '''With great assistance from https://stackoverflow.com/a/39268987'''
    def __init__(self, filename, rpt_title, input, top5, drawing, **kwargs):
        super().__init__(filename, page_size=A4, _pageBreakQuick=0, **kwargs)
        self.rpt_title = rpt_title
        self.input = input

        self.page_width = (self.width + self.leftMargin * 2)
        self.page_height = (self.height + self.bottomMargin * 2)

        styles = getSampleStyleSheet()

        # Setting up the frames, frames are use for dynamic content not fixed page elements
        first_page_frame = Frame(self.leftMargin, self.bottomMargin, 
            self.width, self.height - 3 * cm, id='first_page')
        later_pages_frame = Frame(self.leftMargin, self.bottomMargin, 
            self.width, self.height, id='later_page')
        big_page_frame = Frame(self.leftMargin, self.bottomMargin, 
            self.width, self.height + 2.2 * cm, topPadding=9.9, id='big_page')

        # Creating the page templates
        first_page = PageTemplate(id='FirstPage', 
            frames=[first_page_frame], onPage=self.on_first_page)
        later_pages = PageTemplate(id='LaterPages', 
            frames=[later_pages_frame], onPage=self.add_default_info)
        big_page = PageTemplate(id='BigPage',
            frames=[big_page_frame], onPage=self.add_default_info, 
            pagesize=(1220,880))
        self.addPageTemplates([first_page, later_pages, big_page])

        # Tell Reportlab to use the other template on the later pages,
        # by the default the first template that was added is used for the first page.
        story = [NextPageTemplate(['*', 'LaterPages'])]

        style = getSampleStyleSheet()['Normal']
        t_style = getSampleStyleSheet()['Title']
        b_style = getSampleStyleSheet()['Bullet']
        style.fontName = 'Helvetica'
        t_style.fontName = 'Helvetica'
        b_style.fontName = 'Helvetica'

        intro = Paragraph("From analyzing the provided data we can provide some facts.",
            style)
        totals = ListFlowable(
                    [
                        Paragraph(input[0],b_style),
                        Paragraph(input[1],b_style),
                        Paragraph(input[2],b_style),
                        Paragraph(input[3],b_style)
                    ],
                    bulletType = 'bullet',
                    bulletFontSize = 8,
                    start='circle',
        )
        lnbr = Spacer(1,0.25*inch)

        story.append(intro)
        story.append(lnbr)
        story.append(totals)
        story.append(lnbr)
        text = """Below, you can see the 5 most watched episodes and the
        number of views they received."""
        para = Paragraph(text, style)
        story.append(para)
        story.append(lnbr)
        ranks = [str(x+1) for x in range(5)]
        titles = [re.split('  * ',top5[x])[0] for x in range(5)]
        views = [re.split('  * ',top5[x])[1] for x in range(5)]

        tbldat = [
                ranks,titles,views
                ]
        tbldat = np.transpose(tbldat) #transpose turns tbldat list into a np.array
        tbldat = tbldat.tolist() #so turn it back into a list
        tbldat.insert(0,['Rank','Title','Views']) #add column headers to the start
        tbl = Table(tbldat)
        story.append(tbl)
        story.append(NextPageTemplate('BigPage'))
        story.append(PageBreak())
        story.append(drawing)

        self.title=rpt_title
        self.author='Jeremiah Adams'
        self.subject='Stats and graphs on the user\'s supplied Netflix activity'
        self.keywords='Netflix DataScience Statistics'

        self.build(story,canvasmaker=NumberedCanvas)

    def on_first_page(self, canvas, doc):
        canvas.saveState()
        # Add the logo and other default stuff
        #self.add_default_info(canvas, doc)
        canvas.setFont('Helvetica', 34)

        canvas.drawCentredString(.5 * doc.page_width, doc.height + 2 * cm, 
            self.rpt_title)

        canvas.restoreState()

    def add_default_info(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setStrokeColor(colors.black, alpha=0.2)
        canvas.setFillColor(colors.black, alpha=0.4)
        canvas.drawString(canvas._pagesize[0] - 4.1 * cm, 
            doc.page_height - 0.5 * cm, self.rpt_title)

        canvas.restoreState()

def pdf_report(pdf_name,input,drawing):
    doc = BaseDocTemplate(pdf_name, showBoundary=1, pagesize=letter)
    #pdfmetrics.registerFont(TTFont('Montserrat', 'Montserrat-Regular.ttf'))

    frameT = Frame(
        doc.leftMargin, 
        doc.bottomMargin, 
        doc.width, 
        doc.height, 
        id='normal'
    )

    frame1 = Frame(
        doc.leftMargin, 
        doc.bottomMargin, 
        doc.width / 2 - 6, 
        doc.height, 
        id='col1'
    )
    frame2 = Frame(
        doc.leftMargin + doc.width / 2 + 6, 
        doc.bottomMargin, 
        doc.width / 2 - 6, 
        doc.height, 
        id='col2'
    )

    doc.addPageTemplates([
        PageTemplate(id='OneCol', frames=frameT),
        PageTemplate(id='TwoCol', frames=[frame1, frame2]),
        PageTemplate(id='BigDrw', frames=frameT, pagesize=(1120,780)),
    ])

    style = getSampleStyleSheet()['Normal']
    t_style = getSampleStyleSheet()['Title']
    b_style = getSampleStyleSheet()['Bullet']
    style.fontName = 'Helvetica'
    t_style.fontName = 'Helvetica'
    b_style.fontName = 'Helvetica'

    title = Paragraph("Netflix Activity Analysis", t_style)
    intro = Paragraph("From analyzing the provided data we can provide some facts.",
            style)
    totals = ListFlowable(
                [
                    Paragraph(input[0],b_style),
                    Paragraph(input[1],b_style),
                    Paragraph(input[2],b_style),
                    Paragraph(input[3],b_style)
                ],
                bulletType = 'bullet',
                bulletFontSize = 8,
                start='circle',
    )
    lnbr = Spacer(1,0.25*inch)
    elements = []
    elements.append(title)
    elements.append(NextPageTemplate('TwoCol'))
    elements.append(PageBreak())
    elements.append(Paragraph("Frame two columns,  " * 500, style))
    elements.append(NextPageTemplate('testpage'))
    elements.append(PageBreak())
    elements.append(drawing)

    # start the construction of the pdf
    doc.build(elements, canvasmaker=NumberedCanvas)

def generate(filename, title, paragraph):
    styles = getSampleStyleSheet()
    report = SimpleDocTemplate(filename)
    report_title = Paragraph(title, styles["h1"])
    report_info = Paragraph(paragraph, styles["BodyText"])
    empty_line = Spacer(1,20)
    report.build([report_title, empty_line, report_info, empty_line])