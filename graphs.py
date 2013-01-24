import ROOT as r

def labelAxis(h = None, labels = {}) :
    h.SetStats(False)
    yaxis = h.GetYaxis()
    for iBin,label in labels.iteritems() :
        yaxis.SetBinLabel(iBin, label)
    yaxis.SetLabelSize(2.0*yaxis.GetLabelSize())

def xMax(graph = None, iPoint = 40) :
    N = graph.GetN()
    iPoint = min(iPoint, N-1)
    x = r.Double()
    y = r.Double()
    graph.GetPoint(iPoint, x, y)
    return float(x)

def magnify(h, factor = 1.0) :
    for axis in [h.GetXaxis(), h.GetYaxis()] :
        axis.SetLabelSize(factor*axis.GetLabelSize())
        axis.SetTitleSize(factor*axis.GetTitleSize())

def adjustPad(pad = r.gPad, logY = False) :
    r.gPad.SetLeftMargin(0.25)
    r.gPad.SetBottomMargin(0.25)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    if logY : r.gPad.SetLogy()

def stylize(h) :
    h.SetStats(False)
    h.SetMinimum(0.5)
    magnify(h, factor = 2.0)
    h.SetLineWidth(2)

def makeSummaryPdf(labels = [], pdf = "summary.pdf") :
    canvas = r.TCanvas()
    canvas.Print(pdf+"[")

    pad0 = r.TPad("pad0", "pad0", 0.1, 0.9, 0.9, 1.0)
    pad1 = r.TPad("pad1", "pad1", 0.1, 0.7, 0.9, 0.9)
    pad2 = r.TPad("pad2", "pad2", 0.1, 0.1, 0.5, 0.5)
    pad3 = r.TPad("pad3", "pad3", 0.5, 0.1, 0.9, 0.5)

    pad0.Draw()
    pad1.Draw()
    pad2.Draw()
    pad3.Draw()

    for label in labels :
        f = r.TFile("root/%s.root"%label)

        #label
        pad0.cd()
        text = r.TText(0.5, 0.5, label.replace("Run2", "Run 2"))
        text.SetNDC()
        text.SetTextAlign(22)
        text.SetTextSize(10.0*text.GetTextSize())
        text.Draw()

        #category graph
        pad1.cd()
        adjustPad()

        graph = f.Get("category_vs_time")
        null = r.TH2D("null", ";time (minutes)", 1, 0.0, 1.1*xMax(graph), 3, 0.5, 3.5)
        null.Draw()
        magnify(null, factor = 3.0)

        t = graph.GetTitle().split("_")
        labelAxis(null, labels = {1:t[0], 2:t[1], 3:t[2]})
        graph.SetMarkerStyle(20)
        graph.SetMarkerColor(r.gStyle.GetHistLineColor())
        graph.SetMarkerSize(0.5*graph.GetMarkerSize())
        graph.Draw("psame")

        pad2.cd()
        adjustPad(logY = True)
        h2 = f.Get("deltaOrN")
        if h2 :
            h2.Draw("hist")
            stylize(h2)

        pad3.cd()
        adjustPad(logY = True)
        h3 = f.Get("deltaBcN")
        if h3 :
            h3.Draw("hist")
            stylize(h3)

        canvas.Print(pdf)
        f.Close()
    canvas.Print(pdf+"]")
