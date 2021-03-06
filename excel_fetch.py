import uuid
import gspread

from os.path import join, dirname, abspath
import xlrd

import seeds
from database import db_session
from manage import State, Day
from rabbit import Rabbit

date=["2020/04/25",
      "2020/04/26",
      "2020/04/27",
      "2020/04/28",
      "2020/04/29",
      "2020/04/30",
      "2020/05/01",
      "2020/05/02",
      "2020/05/03",
      "2020/05/04",
      "2020/05/05",
      "2020/05/06",
      "2020/05/07",
      "2020/05/08",
      "2020/05/09",
      "2020/05/10",
      "2020/05/11",
      "2020/05/12",
      "2020/05/13",
      "2020/05/14",
      "2020/05/15",
      "2020/05/16",
      "2020/05/17",
      "2020/05/18",
      "2020/05/19",
      "2020/05/20",
      "2020/05/21",
      "2020/05/22",
      "2020/05/23",
      "2020/05/24"]
class ExcelFetch(object):
    def fetch(self, country_id):

        fname = join(dirname(dirname(abspath(__file__))), 'ramdhan-api/data', 'ramadan_timetable_sheet.xlsx')
        work_book = xlrd.open_workbook(fname)

        country_id = str(country_id)
        for ws_count, worksheet in enumerate(work_book.sheet_names()):
            # TODO write State By Country Here

            state_district = seeds.get_state_name(worksheet)
            state_name="{0}/{1}".format(state_district[0],state_district[1])
            state_id = str(uuid.uuid4().hex)
            state = State(id=state_id, object_id=state_id, country_id=str(country_id), name_mm_uni=str(state_name),
                          name_mm_zawgyi=Rabbit.uni2zg(state_name))
            sheet=work_book.sheet_by_index(ws_count)
            cal_day_list = sheet.col_values(0)
            hij_day_list = sheet.col_values(1)
            sehri_time_list = sheet.col_values(2)
            iftari_time_list = sheet.col_values(3)

            db_session.add(state)
            db_session.commit()
            for i, (cal_day, hij_day, seh_time, iftar_time) in enumerate(
                    zip(cal_day_list, hij_day_list, sehri_time_list, iftari_time_list)):
                if i is not 0:
                    article_id = str(uuid.uuid4().hex)
                    article = Day(id=article_id, object_id=article_id,
                                  country_id=str(country_id),
                                  state_id=str(state.object_id),
                                  day=i, day_mm=str(seeds.get_mm_num(i)), sehri_time=str(str(seh_time).strip() + " am"),
                                  sehri_time_desc="Sehri",
                                  calendar_day=str(date[i-1]),
                                  hijari_day=str(hij_day).strip(),
                                  sehri_time_desc_mm_zawgyi=Rabbit.uni2zg("ဝါချည်ချိန်"),
                                  sehri_time_desc_mm_uni="ဝါချည်ချိန်",
                                  iftari_time=str(str(iftar_time).strip() + " pm"),
                                  dua_mm_uni=Rabbit.zg2uni(seeds.daily_dua(i)["dua_mm"]),
                                  dua_mm_zawgyi=Rabbit.uni2zg(seeds.daily_dua(i)["dua_mm"]),
                                  dua_ar=seeds.daily_dua(i)["dua_ar"],
                                  dua_en=seeds.daily_dua(i)["dua_en"],
                                  iftari_time_desc="Iftari",
                                  iftari_time_desc_mm_zawgyi=Rabbit.uni2zg("ဝါဖြေချိန်"),
                                  iftari_time_desc_mm_uni="ဝါဖြေချိန်")

                    db_session.add(article)
                    db_session.commit()
                    fetch_state = True

        return fetch_state
