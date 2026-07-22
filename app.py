import os
import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    page_title="Improvement Opportunity Form", page_icon="💡", layout="wide"
)

# --- تفعيل اتجاه الصفحة من اليمين لليسار (RTL) للغة العربية ---
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .stApp {
        direction: rtl;
        text-align: right;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stCheckbox, .stRadio {
        text-align: right !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        direction: rtl;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- الاتصال بقاعدة بيانات Google Sheets ---
@st.cache_resource
def init_connection():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]
  # التأكد من وجود ملف الـ credentials.json
  creds = ServiceAccountCredentials.from_json_keyfile_name(
      "credentials.json", scope
  )
  client = gspread.authorize(creds)
  # اكتب هنا اسم ملف جوجل شيت الذي أنشأته تماماً
  sheet = client.open("Improvement_Database").sheet1
  return sheet

try:
  sheet = init_connection()
except Exception as e:
  st.error(f"خطأ في الاتصال بقاعدة البيانات السحابية: {e}")

# تحميل الورش والخطوط من الملف المحلي أو الافتراضي
@st.cache_data
def load_excel_data():
  try:
    df = pd.read_excel("Kaizen data.xlsx")
    return df
  except Exception as e:
    return None

df_kaizen = load_excel_data()

st.title("💡 استمارة فرصة تحسين - Improvement Opportunity Form")
st.markdown("Groupe Atlantic - We G.A (Water Heater Business Unit - Production Department)")

with st.form("kaizen_form"):
  col1, col2 = st.columns(2)

  with col1:
    emp_name = st.text_input("اسم الموظف / Employee Name")
    emp_code = st.text_input("الكود الوظيفي / Employee Code")
    date = st.date_input("التاريخ / Date")

  with col2:
    emp_job = st.text_input("الوظيفة / Job Title")

    if df_kaizen is not None:
      lines = df_kaizen["Line"].dropna().astype(str).unique().tolist()
      workshops = df_kaizen["Workshop"].dropna().astype(str).unique().tolist()

      selected_line = st.selectbox(
          "الخط / Line", lines, index=None, placeholder="اختر الخط / Select Line"
      )
      selected_workshop = st.selectbox(
          "الورشة / Workshop", workshops, index=None, placeholder="اختر الورشة / Select Workshop"
      )
    else:
      selected_line = st.text_input("الخط / Line (تعذر قراءة ملف الأكسل)")
      selected_workshop = st.text_input("الورشة / Workshop (تعذر قراءة ملف الأكسل)")

  problem_desc = st.text_area("شرح المشكلة / Problem Description")
  solution_desc = st.text_area("شرح الفكرة / الحل - Idea / Solution Description")

  uploaded_image = st.file_uploader(
      "صورة توضيحية للمشكلة / Problem Illustration Image",
      type=["jpg", "png", "jpeg"],
  )

  st.markdown("---")

  st.markdown("**التأثير على عوامل التحسين (اختر واحد أو أكثر) / Improvement Factors:**")
  col_f1, col_f2 = st.columns(2)
  with col_f1:
    factor_safety = st.checkbox("السلامة والصحة المهنية / Safety")
    factor_quality = st.checkbox("الجودة / Quality")
    factor_prod = st.checkbox("الإنتاج / Production")
  with col_f2:
    factor_cost = st.checkbox("التكلفة / Cost")
    factor_5s = st.checkbox("5S")
    factor_ergonomics = st.checkbox("توظيف الحركة - إرجونومكس / Ergonomics")

  st.markdown("---")

  st.markdown("**التأثير على الفواقد (اختر واحد أو أكثر) / Waste Impact:**")
  col_w1, col_w2 = st.columns(2)
  with col_w1:
    waste_defects = st.checkbox("العيوب / Defects")
    waste_overproduction = st.checkbox("الإنتاج الزائد / Overproduction")
    waste_waiting = st.checkbox("الانتظار / Waiting")
    waste_skills = st.checkbox("المهارات الغير مستغلة / Underutilized Skills")
  with col_w2:
    waste_transport = st.checkbox("النقل / Transportation")
    waste_inventory = st.checkbox("المخزون / Inventory")
    waste_motion = st.checkbox("الحركة / Motion")
    waste_overprocessing = st.checkbox("الإفراط في التشغيل / Overprocessing")

  submit_button = st.form_submit_button(label="حفظ وإرسال الاستمارة / Save & Submit")

  if submit_button:
    if not emp_name or not emp_code:
      st.warning("يرجى إدخال اسم الموظف والكود على الأقل. / Please enter employee name and code.")
    elif not selected_line or not selected_workshop:
      st.warning("يرجى اختيار الخط والورشة. / Please select line and workshop.")
    else:
      os.makedirs("improvement_images", exist_ok=True)
      image_path = "لا يوجد / None"
      if uploaded_image is not None:
        image_path = os.path.join("improvement_images", uploaded_image.name)
        with open(image_path, "wb") as f:
          f.write(uploaded_image.getbuffer())

      # حساب الكود التالي تلقائياً من جوجل شيت
      try:
        existing_data = sheet.get_all_records()
        if existing_data:
          df_existing = pd.DataFrame(existing_data)
          if "كود الفرصة" in df_existing.columns and not df_existing["كود الفرصة"].empty:
            # تنظيف القيم وتحويلها لرقم لتجنب الأخطاء
            max_val = pd.to_numeric(df_existing["كود الفرصة"], errors='coerce').max()
            next_code = int(max_val) + 1 if pd.notna(max_val) else 11411
          else:
            next_code = 11411
        else:
          next_code = 11411
      except:
        next_code = 11411

      row_data = [
          next_code,
          str(date),
          emp_name,
          str(emp_code),
          emp_job,
          str(selected_line),
          str(selected_workshop),
          problem_desc,
          solution_desc,
          image_path,
          "نعم" if factor_safety else "لا",
          "نعم" if factor_quality else "لا",
          "نعم" if factor_prod else "لا",
          "نعم" if factor_cost else "لا",
          "نعم" if factor_5s else "لا",
          "نعم" if factor_ergonomics else "لا",
          "نعم" if waste_defects else "لا",
          "نعم" if waste_overproduction else "لا",
          "نعم" if waste_waiting else "لا",
          "نعم" if waste_skills else "لا",
          "نعم" if waste_transport else "لا",
          "نعم" if waste_inventory else "لا",
          "نعم" if waste_motion else "لا",
          "نعم" if waste_overprocessing else "لا",
      ]

      # إضافة الصف الجديد مباشرة إلى جوجل شيت السحابي
      sheet.append_row(row_data)

      st.success(
          f"✅ تم حفظ استمارة فرصة التحسين بنجاح في السحابة برقم الكود: **{next_code}** 🎉"
      )
