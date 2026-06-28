import re
import textwrap
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
    TableStyle,
    KeepTogether
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
    def __init__(self, filename, rpt_title, input, drawing, *args, **kwargs):
        super().__init__(filename, page_size=A4, _pageBreakQuick=0, **kwargs)
        self.rpt_title = rpt_title
        self.input = input
        countTop = len(args)
        if not countTop > 0:     
            overallTop = "No data available"
        else:
            # Set four variables to first four of args, or None if args is finished/empty
            #overallTop,tvTop,epTop,indEpTop,movTop,specTop = (args + (None,) * 6)[:6]
            overallTop,tvTop,epTop,indEpTop,movTop,specTop = args[0]
            

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

        intro = Paragraph("From analyzing the provided data we have gleaned some facts.",
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
        #text = """Below, you can see the %s most watched items and the
        #number of views they received.""" % (top_num)
        story.append(story_builder(story,style,overallTop,tvTop,epTop,indEpTop,movTop,specTop))
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

def tbl_prep(topItem,top_num,itemContext):
    ranks = [str(x+1) for x in range(top_num)]
    titles = [re.split('  * ',topItem[x])[0] for x in range(top_num)]
    views = [re.split('  * ',topItem[x])[1] for x in range(top_num)]
    episodes = []
    tbldat = [
            ranks,titles,views
            ]
    tblhead = ['Rank','Title','Views']
    columnWidths = [None,150,None]
    styleCommands = [
        # Outer grid
        ('LINEABOVE',(0,0),(-1,0),0.25,colors.black),
        ('LINEBELOW',(0,0),(-1,0),0.25,colors.black),
        ('LINEBEFORE',(0,0),(0,-1),0.25,colors.black),
        ('LINEAFTER',(0,0),(0,-1),0.25,colors.black),
        ('LINEBELOW',(0,-1),(-1,-1),0.25,colors.black),
        ('LINEAFTER',(-1,0),(-1,-1),0.25,colors.black),
        ('LINEAFTER',(-2,0),(-2,-1),0.25,colors.black),
        # Keep it together on the page
        ('NOSPLIT',(0,0),(-1,-1)),
        # Aligning rank and views columns
        ('ALIGN',(0,1),(0,-1),'CENTER'),
        ('ALIGN',(-1,1),(-1,-1),'RIGHT'),
        # Needed due to splitting long Titles
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E50914')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#E7E7E7'),colors.HexColor('#EEEEEE')])
    ]
    is_tv = re.search('(most watched|TV show) episodes*',itemContext)
    seasonMark = [re.search('Season \d+',topItem[x]) for x in range(top_num)]
    individualized = False
    if any(item is not None for item in seasonMark):
        individualized = True
    if is_tv:
        if individualized == True:
            episodes = [re.split('  * ',topItem[x])[0] for x in range(top_num)]
            titles = [re.split('  * ',topItem[x])[1] for x in range(top_num)]
            seasons = [re.split('  * ',topItem[x])[2] for x in range(top_num)]
            views = [re.split('  * ',topItem[x])[3] for x in range(top_num)]
            tbldat = [
                    ranks,episodes,titles,seasons,views
                    ]
            tblhead = ['Rank','Episode','Title','Season','Views']
            columnWidths = [None,150,150,None,None]
            styleCommands.extend([
                ('LINEAFTER',(1,0),(1,-1),0.25,colors.black),
                ('LINEAFTER',(2,0),(2,-1),0.25,colors.black),
            ])
        else:
            episodes = [re.split('  * ',topItem[x])[1] for x in range(top_num)]
            views = [re.split('  * ',topItem[x])[2] for x in range(top_num)]
            tbldat = [
                    ranks,titles,episodes,views
                    ]
            tblhead = ['Rank','Title','Episode','Views']
            columnWidths = [None,150,150,None]
            styleCommands.append(
                ('LINEAFTER',(1,0),(1,-1),0.25,colors.black)
            )
    """ for x in range(top_num):
        pos = titles[x].find('-')
        #Conditionally add columns may be better
        if pos != -1 and is_tv:
            showName = titles[x][:pos]
            episodeName = titles[x][pos:]
            if len(episodeName) > 33:
                episodeName = episodeName[:33] + '\n' + episodeName[33:]
            titles[x] = showName + '\n' + episodeName
        elif len(titles[x]) > 30:
            titles[x] = titles[x][:30] + '\n' + titles[x][30:] """
    #t = Table(data, colWidths=[100, 100], rowHeights=row_heights)
    '''Somewhere before here, need a var or something to dictate number of columns
    and then conditionally add to tblhead and tbldat'''
    for list in titles,episodes:
        for x in range(len(list)):
            list[x] = textwrap.fill(list[x], width=30)
            '''if len(list[x]) > 30:
                list[x] = list[x][:30] + '\n' + list[x][30:]'''
    tbldat = np.transpose(tbldat) #transpose turns tbldat list into a np.array
    tbldat = tbldat.tolist() #so turn it back into a list
    tbldat.insert(0,tblhead) #add column headers to the start
    tbl = Table(tbldat, colWidths=columnWidths)
    tbl.setStyle(TableStyle(styleCommands))
    return tbl

def story_builder(story,style,top1,top2,top3,top4,top5,top6):
    '''As long as topPiece is passed, add it to the story in this way'''
    has_added = False
    for top in (top1,top2,top3,top4,top5,top6):
        if not top is None:
            # has_added to prevent trailing lnbr
            if has_added:
                    story.append(lnbr)
            story = story
            lnbr = Spacer(1,0.25*inch)
            top_num = len(top[0])
            text = top[1]
            para = Paragraph(text, style)
            tbl = tbl_prep(top[0],top_num,top[1])
            group = KeepTogether([para,lnbr,tbl])
            story.append(group)
            has_added = True