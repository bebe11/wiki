#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from bs4 import BeautifulSoup
from flask import Flask, json, make_response, redirect, render_template, request, send_file, url_for
import io
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import urllib # .request

app = Flask(__name__)

table_id = None
table_list = []


def read_html(url):
    htmlfile = urllib.request.urlopen(url)
    htmltext = htmlfile.read()
    htmlfile.close()
    return htmltext


def col_span_cnt(th):
    try:
        col = int(th["colspan"])
    except (ValueError, KeyError) as e:
        col = 1
    return col


def row_span_cnt(th):
    try:
        rw = int(th["rowspan"])
    except (ValueError, KeyError) as e:
        rw = 1
    return rw


def find_href_tag(td):
    aTags = td.findAll('a', attrs={'href': re.compile("^/wiki/")})
    if aTags:
        for aTag in aTags:
            if aTag.img is None:
                return aTag.attrs['title']
    else:
        return td.text


def find_tables(tables):
    table_list.clear()
    for table in tables:
        row_list = []
        temp_header = []
        temp_list = []
        has_row_span = False
        for tr_index, tr in enumerate(table.find_all("tr")):
            is_last_value = False
            more_row = False 
            datas = []
            count = 0

            for th_index, th in enumerate(tr.find_all('th')):
                row_span = row_span_cnt(th)
                col_span = col_span_cnt(th)
                data = th.text.replace('\xa0', '').strip("\n")
                if col_span > 1:
                    for x in range(0, col_span):
                        count += 1
                        datas.append(data)
                else:
                    for i in temp_header:
                        if i['tr_index'] != tr_index:
                            if i['th_index'] == count:
                                datas.append(i['value'])
                                count += 1
                            if th_index == len(tr.find_all('th')) - 1 and is_last_value == False:
                                is_last_value = True
                                datas.append(data)
                                count += 1
                    if is_last_value == False:
                        datas.append(data)
                    if row_span > 1:
                        has_row_span = True
                        temp_header.append({'value' : th.text, 'count' : row_span, 'th_index' : count, 'tr_index' : tr_index})
                    count += 1

            for td_index, td in enumerate(tr.find_all('td')):
                td_length = len(tr.find_all('td'))
                empty_span = td.find_all("span")
                row_span = row_span_cnt(td)
                has_match = False
                data = ''
                if empty_span:
                    data = find_href_tag(td)
                else:
                    data = td.text.replace('\xa0', '').strip("\n")
                      
                for tempIndex, i in enumerate(temp_list): 
                    if more_row:
                        if i['th_index'] - 1 == td_index:
                            has_match = True
                        if td_index == td_length - 1:
                            if i['th_index'] - 2 == td_index:
                                is_last_value = True
                                has_match = True
                    else:
                        if i['th_index'] == td_index:
                            more_row = True
                            has_match = True
                        if td_index == td_length - 1:
                            if i['th_index'] - 1 == td_index:
                                is_last_value = True
                                has_match = True
                    if has_match:
                        if is_last_value:
                            datas.append(data)
                        datas.append(i['value'])
                        i['count'] = i['count'] - 1
                        if i['count'] == 1:
                            del temp_list[tempIndex]
                        has_match = False
                                          
                if is_last_value == False:
                    datas.append(data)
                if row_span > 1:
                    temp_list.append({'value' : data, 'count' : row_span, 'th_index' : td_index, 'tr_index' : tr_index})
            row_list.append(datas)
        df = pd.DataFrame(row_list[1:], columns=row_list[0])
        if has_row_span:
            temp_lista = []
            temp_dict = {}
            for i, ertek in enumerate(df.iloc[0]):
                temp_ertek = df.columns[i] + "(" + ertek + ")"
                temp_lista.append(temp_ertek)
                temp_dict[df.columns[i]] = temp_ertek
            df.columns = temp_lista
            df = df[1:]
        # table_list.append(df.to_html(index = False, classes = ["table","table-bordered"]).replace('border="1"','border="0"'))
        table_list.append(df)


def get_tables_html():
    table_html = ''
    for i, table in enumerate(table_list):
        table = table.to_html(index = False, classes = ["table", "table-bordered"]).replace('border="1"', 'border="0" id="table' + str(i) + '"')
        if (i + 1) % 2 == 0:
            table_div = '<div style="overflow-y: hidden;max-height: 300px; padding-top: 20px"  class="col-md-5 md-offset-2">' + table
        else:
            table_div = '<div style="overflow-y: hidden;max-height: 300px; padding-top: 20px"  class="col-md-5">' + table
        table_html += table_div + '</div>'
    return table_html


def get_single_table_html(df):
    return df.to_html(index = False, classes = ["table", "table-bordered"]).replace('border="1"', 'border="0" id="selectedTable"')

    
def get_single_table_csv(df):
    return df.to_csv(sep=",", index=False, encoding="utf-8", date_format="%Y-%m-%d")


@app.route('/')
def wiki():
    return render_template('wiki.html')


@app.route('/getWikiTables', methods=['POST'])
def get_wiki_tables():
    url = request.form['url']
    htmltext = read_html(url)
    page = BeautifulSoup(htmltext, 'html.parser')
    tables = page.find_all("table", attrs={"class": "wikitable"})
    find_tables(tables)
    return get_tables_html()


@app.route('/getTable', methods=['POST'])
def get_table():
    global table_id
    table_id = int(request.form['table_id'].split('table')[1])
    #table_id = request.form['radioTable']
    return get_single_table_html(table_list[table_id])
    
@app.route('/vizType', methods=['POST', 'GET'])
def get_viz():
    result = request.form
    viz = result["viz"]
    o_sor = [int(result["x"])]
    o_ertek = [int(result["y"])]
    feliratok = {x: result[x].strip() for x in ["title", "xTitle", "yTitle"]}
    if request.method == "POST":
        g = grafikon(grafikon_tipus=viz, o_sor=o_sor, o_ertek=o_ertek, grafikon_aggr=result["aggregate"], feliratok=feliratok)
    else:
        g = grafikon(grafikon_tipus="bar", o_sor=o_sor, o_ertek=o_ertek, grafikon_aggr=result["aggregate"], feliratok=feliratok)
    gq = base64.b64encode(g).decode("utf-8").replace("\n", "")
    return '<img src="data:image/png;base64,{}"/>'.format(gq)


def grafikon(grafikon_tipus, o_sor, o_ertek, grafikon_aggr, feliratok):
    
    print("o_sor:", o_sor, str(type(o_sor)))
    print("o_ertek:", o_ertek, str(type(o_ertek)))
    
    aggr_options = ["np.size", "np.sum", "np.min", "np.max", "np.mean"]
    grafikon_aggr_obj = None
    if grafikon_aggr is None or grafikon_aggr not in aggr_options:
        pass
    else:
        grafikon_aggr_obj = eval(grafikon_aggr)
    
    o_kell = list(set(set(o_sor) | set(o_ertek))) # az oszlopok indexei, amire (bármilyen célból) szükségünk lesz
    jelmagyarazat = len(o_ertek) > 1 # akkor kell jelmagyarázat, ha egynél több adatsort tartalmaz az anyag
    o_sor_str = ""
    if o_sor:
        for c in o_sor:
            o_sor_str += "adf.columns[{}], ".format(c)
        o_sor_str = "[" + o_sor_str[:-2] + "]" # az utolsó vessző és szóköz persze már ne maradjon benne

    # az előkészületek után irány a Pandas
    adf = table_list[table_id]
    adf = adf.apply(lambda x: pd.to_numeric(x, errors="ignore"), axis=0) # számmá alakítjuk, amit lehet
    print(adf.info())
    print("adf hossza:", len(adf))
    o_sor_obj = eval(o_sor_str) # már létezik adf objektum, itt már ki lehet értékelni
    
    agb = adf.iloc[:, o_kell].groupby(o_sor_obj)
    agba = agb.aggregate(grafikon_aggr_obj)
    print("agba hossza:", len(agba))
    
    if grafikon_tipus == "line":
        ch = agba.plot(kind="line", legend=jelmagyarazat)
    elif grafikon_tipus == "pie":
        ch = agba.plot(kind="pie", subplots=True, legend=jelmagyarazat)
    elif grafikon_tipus == "area":
        ch = agba.plot(kind="area", legend=jelmagyarazat)
    elif grafikon_tipus == "bar":
        ch = agba.plot(kind="bar", legend=jelmagyarazat)
    elif grafikon_tipus == "bar_stacked":
        ch = agba.plot(kind="bar", stacked=True, legend=jelmagyarazat)
    elif grafikon_tipus == "barh":
        ch = agba.plot(kind="barh", legend=jelmagyarazat)
    elif grafikon_tipus == "barh_stacked":
        ch = agba.plot(kind="barh", stacked=True, legend=jelmagyarazat)
    else:
        ch = None
    
    if jelmagyarazat:
        plt.legend(loc="best")
    if feliratok.get("title"):
        plt.title(feliratok.get("title"))
    if feliratok.get("xTitle"):
        plt.xlabel(feliratok.get("xTitle"))
    if feliratok.get("yTitle"):
        plt.ylabel(feliratok.get("yTitle"))
    plt.tight_layout()
    fig = plt.gcf()
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    eimg = img.getvalue() # .encode("base64")
    return eimg
    
    # agba.plot()
    # fig = plt.gcf()
    # fig.set_size_inches(12, 8)
    # ax = fig.gca()
    # ax.grid(b=True, which="major", color="b", linestyle=":", linewidth=1, alpha=0.1)
    # plt.title("Na hogyan alakul?")
    # plt.xlabel("X tengely")
    # plt.ylabel("Y tengely")


if __name__== "__main__":
    app.run(debug=True)
