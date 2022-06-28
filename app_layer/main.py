from operator import index
import re
from fastapi import FastAPI, Request
import pyodbc
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
templates = Jinja2Templates(directory="templates")


# PRODUKCJA



# LOKALNIE MATEUSZ GT166
DB = "DBADAL"
DB_SERVER = "GT166\SQLEXPRESS01"
DB_USER = "sa"
DB_PASSWORD = "czosnek20"
DB_DRIVER = "{ODBC Driver 17 for SQL Server}"

db_URL = (f"DRIVER={DB_DRIVER};"
          f"Server={DB_SERVER};"
          f"Database={DB};"
          f"UID={DB_USER};"
          f"PWD={DB_PASSWORD};"
          # "Trusted_Connection=yes;"
          )

buffor1_view_glob = []
buffor2_view_glob = []

@app.get('/', tags=["GetFromView"], response_class=HTMLResponse)
def get_programs(request: Request):
    buffor1_view = []
    buffor2_view = []
    tmp1 = []
    try:
        conn = pyodbc.connect(db_URL)
        query_last_1 = f"""SELECT TOP (1)[IloscBelek]
                            FROM [{DB}].[dbo].[listabufor] where NrToru = 1 order by DataMod desc"""
        query_last_2 = f"""SELECT TOP (1)[IloscBelek]
                            FROM [{DB}].[dbo].[listabufor] where NrToru = 2 order by DataMod desc"""
        cursor = conn.cursor()
        cursor.execute(query_last_1)
        amount_of_row1 = cursor.fetchone()
        cursor.execute(query_last_2)
        amount_of_row2 = cursor.fetchone()
        
        query_buffor_1 = f"""SELECT TOP ({amount_of_row1[0]})
                                ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS Lp,
                                bu.NrPRM, pr.NazwaProgramu, bu.DataMod
                                FROM dbo.listabufor as bu, dbo.programy as pr
                                WHERE bu.NrPRM = pr.NrPRM and bu.StatusBelki = 1 and bu.NrToru = 1 order by bu.DataMod desc"""  
        
        query_buffor_2 = f"""SELECT TOP ({amount_of_row2[0]})
                                ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS Lp,
                                bu.NrPRM, pr.NazwaProgramu, bu.DataMod
                                FROM dbo.listabufor as bu, dbo.programy as pr
                                WHERE bu.NrPRM = pr.NrPRM and bu.StatusBelki = 1 and bu.NrToru = 2 order by bu.DataMod desc"""   
        
        query_counters_list = """SELECT * FROM [dbo].[packdetail]"""                                
        cursor.execute(query_buffor_1)
        buffor1 = cursor.fetchall()
        cursor.execute(query_buffor_2)
        buffor2 = cursor.fetchall()
        cursor.execute(query_counters_list)
        multiples = cursor.fetchall()                     
        conn.close()
    except pyodbc.OperationalError:
        conn.close()
        return HTMLResponse("__Server MSSQL is not found or not accessible__")
    lp1 = 1
    
    for belka in buffor1:
        idx = buffor1.index(belka)
        
        name = buffor1[idx][2]
        data = buffor1[idx][3]
        NrPRM = buffor1[idx][1] 
        # print("belka", belka)
        # print("NrPRM:", belka[1], "Index:", buffor1.index(belka), "dd:", buffor1[idx][1])
        step = 0
        counter = 0
        max_step = len(buffor1)
        
        # print("max_step:", max_step)
        # idx+step , max_step - czyli tyle ile jest elementów w bufforze oraz sprawdzam nrprm
        while idx+step < max_step and buffor1[idx][1] == buffor1[idx + step][1]:
            step += 1
            counter +=1
            # print("current_idx:", idx)
            # print("step:", step)
            # print("counter:", counter)            
        # print("IDX:", idx)
        
        tmp1.append(NrPRM)
        # print("::len::", len(tmp1))
        # print("detal:", detal)
        if len(tmp1) > 1:
            # print("Czy to je równe:", tmp1[-1], "i to:", buffor1_view[-1][0])
            if tmp1[-1] != buffor1_view[-1][1]:
                buffor1_view.append((lp1, NrPRM, name, counter, data))
                lp1 += 1
            
        else:        
            buffor1_view.append((lp1, NrPRM, name, counter, data))
            lp1 += 1
    # print(":tmp1:", tmp1)                  
    
    for ity in buffor1_view:
        nr = ity[1]
        amount = int(ity[3])
        for el in multiples:
            if el[1] == nr:
                ilosc_detali = amount * int(el[2])
                ilosc_pojemnikow = int((ilosc_detali / int(el[3])) + (ilosc_detali % int(el[3])>0))
                ilosc_zawieszek = amount * int(el[4])
                buffor1_view[buffor1_view.index(ity)] = ity + (ilosc_detali, ilosc_pojemnikow, ilosc_zawieszek)
                do_glob = (ity[1], ity[4], ilosc_detali)
                if do_glob in buffor1_view_glob:
                    break
                else:
                    buffor1_view_glob.append(do_glob)
   
    for ity in list(buffor1_view):
        length = len(ity)
        if length < 6:
            buffor1_view.pop(buffor1_view.index(ity))
        print("<<new on KTL>>:", ity)    
    for ity in list(buffor1_view):
        for record in buffor1_view_glob:
            # print("\nity[1]:", ity[1], "ity[4]:", ity[4])
            # print("rec[0]:", record[0], "rec[1]:", record[1])
            if ity[1] == record[0] and ity[4] == record[1]:
                print(buffor1_view[buffor1_view.index(ity)][2], "TOP:", record[-1])
                buffor1_view[buffor1_view.index(ity)] = ity + (record[-1], )
                break       
    print("Rozmiar buffor1_view_glob, to:", len(buffor1_view_glob), "\n")
    
    buffor1_view_reverse = []
    c = (1)
    for ity in range(len(buffor1_view)-1, -1, -1):
        cc = (c, )
        buffor1_view_reverse.append((cc + buffor1_view[ity][1:]))
        c = c + 1
    
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
    tmp2 = []
    lp2 = 1
    for belka in buffor2:
        idx = buffor2.index(belka)
        
        name = buffor2[idx][2]
        data = buffor2[idx][3]
        NrPRM = buffor2[idx][1] 
        # print("belka", belka)
        # print("NrPRM:", belka[1], "Index:", buffor1.index(belka), "dd:", buffor1[idx][1])
        step = 0
        counter = 0
        max_step = len(buffor2)
        
        # print("max_step:", max_step)
        while idx+step < max_step and buffor2[idx][1] == buffor2[idx + step][1]:
            step += 1
            counter +=1
            # print("current_idx:", idx)
            # print("step:", step)
            # print("counter:", counter)            
        # print("IDX:", idx)
        
        tmp2.append(NrPRM)
        # print("::len::", len(tmp2))
        # print("detal:", detal)
        if len(tmp2) > 1:
            # print("Czy to je równe:", tmp2[-1], "i to:", buffor1_view[-1][0])
            if tmp2[-1] != buffor2_view[-1][1]:
                buffor2_view.append((lp2, NrPRM, name, counter, data))
                lp2 += 1
            
        else:        
            buffor2_view.append((lp2, NrPRM, name, counter, data))
            lp2 += 1
    # print(":tmp2:", tmp2)                  
    
    for ity in buffor2_view:
        nr = ity[1]
        amount = int(ity[3])
        for el in multiples:
            if el[1] == nr:
                ilosc_detali = amount * int(el[2])
                ilosc_pojemnikow = int((ilosc_detali / int(el[3])) + (ilosc_detali % int(el[3])>0))
                ilosc_zawieszek = amount * int(el[4])
                buffor2_view[buffor2_view.index(ity)] = ity + (ilosc_detali, ilosc_pojemnikow, ilosc_zawieszek)
                do_glob = (ity[1], ity[4], ilosc_detali)
                if do_glob in buffor2_view_glob:
                    break
                else:
                    buffor2_view_glob.append(do_glob)
    
    for ity in list(buffor2_view):
        length = len(ity)
        if length < 6:
            buffor2_view.pop(buffor2_view.index(ity))
        print("<<new on PRO>>:", ity)  
    for ity in buffor2_view:
        for record in buffor2_view_glob:
            # print("record2:", record)
            # print("ity2:", ity)
            if ity[1] == record[0] and ity[4] == record[1]:
                print(buffor2_view[buffor2_view.index(ity)][2], "TOP:", record[-1])
                buffor2_view[buffor2_view.index(ity)] = ity + (record[-1], )
                break
    print("Rozmiar buffor2_view_glob, to:", len(buffor2_view_glob), "\n")       
                        
    buffor2_view_reverse = []
    c = (1)
    for ity in range(len(buffor2_view)-1, -1, -1):
        cc = (c, )
        buffor2_view_reverse.append((cc + buffor2_view[ity][1:]))
        c = c + 1
    
    return templates.TemplateResponse("index.html", {"request": request, "buffor1_view": buffor1_view_reverse, "buffor2_view": buffor2_view_reverse,
                                     "amount_of_row1":amount_of_row1, "amount_of_row2":amount_of_row2})

    
    