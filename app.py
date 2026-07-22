import os
import pandas as pd
import streamlit as st

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

# تحميل الورش والخطوط من الملف الأصلي
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

    # استخراج الخطوط والورش من ملف الأكسل بدون اختيار افتراضي
    if df_kaizen is not None:
      lines = (
          df_kaizen["Line"].dropna().astype(str).unique().tolist()
      )
      workshops = (
          df_kaizen["Workshop"].dropna().astype(str).unique().tolist()
      )

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

  # --- خانة رفع الصورة التوضيحية للمشكلة ---
  uploaded_image = st.file_uploader(
      "صورة توضيحية للمشكلة / Problem Illustration Image",
      type=["jpg", "png", "jpeg"],
  )

  st.markdown("---")

  # 1. التأثير على عوامل التحسين (الـ 6 عناصر)
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

  # 2. التأثير على الفواقد (الـ 8 عناصر)
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
      output_file = "Improvement_Submitted_Data.xlsx"
      os.makedirs("improvement_images", exist_ok=True)

      image_path = "لا يوجد / None"
      if uploaded_image is not None:
        image_path = os.path.join("improvement_images", uploaded_image.name)
        with open(image_path, "wb") as f:
          f.write(uploaded_image.getbuffer())

      if os.path.exists(output_file):
        df_existing = pd.read_excel(output_file)
        if (
            not df_existing.empty
            and "كود الفرصة" in df_existing.columns
        ):
          next_code = int(df_existing["كود الفرصة"].max()) + 1
        else:
          next_code = 11411
      else:
        df_existing = pd.DataFrame()
        next_code = 11411

      submission_data = {
          "كود الفرصة": next_code,
          "التاريخ": str(date),
          "اسم الموظف": emp_name,
          "الكود الوظيفي": emp_code,
          "الوظيفة": emp_job,
          "الخط": selected_line,
          "الورشة": selected_workshop,
          "شرح المشكلة": problem_desc,
          "شرح الفكرة / الحل": solution_desc,
          "مسار الصورة": image_path,
          "السلامة والصحة المهنية": "نعم" if factor_safety else "لا",
          "الجودة": "نعم" if factor_quality else "لا",
          "الإنتاج": "نعم" if factor_prod else "لا",
          "التكلفة": "نعم" if factor_cost else "لا",
          "5S": "نعم" if factor_5s else "لا",
          "توظيف الحركة - إرجونومكس": "نعم" if factor_ergonomics else "لا",
          "العيوب": "نعم" if waste_defects else "لا",
          "الإنتاج الزائد": "نعم" if waste_overproduction else "لا",
          "الانتظار": "نعم" if waste_waiting else "لا",
          "المهارات الغير مستغلة": "نعم" if waste_skills else "لا",
          "النقل": "نعم" if waste_transport else "لا",
          "المخزون": "نعم" if waste_inventory else "لا",
          "الحركة": "نعم" if waste_motion else "لا",
          "الإفراط في التشغيل": "نعم" if waste_overprocessing else "لا",
      }

      df_new = pd.DataFrame([submission_data])
      df_combined = pd.concat([df_existing, df_new], ignore_index=True)
      df_combined.to_excel(output_file, index=False)

      st.success(
          f"✅ تم حفظ استمارة فرصة التحسين بنجاح برقم الكود: **{next_code}** 🎉"
      )