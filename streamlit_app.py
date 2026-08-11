import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

##################################################
st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem; /* Thay đổi số rem này nhỏ hơn (ví dụ 1rem hoặc 2rem) */
        }
    </style>
""", unsafe_allow_html=True)

st.subheader("Thời Khóa Biểu THPT APC")

##################################################

# Giả sử df đã có các cột: Thu, Tiet, Lop_6A1, Lop_7A1, ...
# Hàm tạo lịch cho một giáo viên
def build_teacher_schedule(dfxet, teacher_name):
    schedule = {"Tiết": list(range(1, 11))}
    
    # Duyệt qua các thứ (2..7)
    for thu in range(2, 8):
        list_lopmon = []
        for tiet in range(1, 11):
            row = df[(df["Thu"] == thu) & (df["Tiet"] == tiet)]
            lopmon = []
            for col in df.columns:
                if col.startswith("Lop_"):
                    val = row[col].values
                    if len(val) > 0 and pd.notna(val[0]) and teacher_name in val[0]:
                        # Ghép dạng "Lop_xxx - Mon"
                        lopmon.append(val[0])
            # Nếu có nhiều lớp thì nối bằng dấu ",", nếu không thì ""
            list_lopmon.append(", ".join(lopmon) if lopmon else "")
        schedule[f"Thứ {thu}"] = list_lopmon
    
    #print(schedule)
    #show_dict_popup(schedule)
    return schedule


def update_bang_yctrt():
    pass

def xep_lai_tkb():
    st.write('Tien da xep lai xong va da luu cap nhat TKB')

def show_timetable(df):
    custom_css = {
        ".my-blue-header": {
            "background-color": "#0d47a1 !important",
            "color": "#ffffff !important",
            "font-weight": "bold !important"
        },
        ".my-blue-header .ag-header-cell-text": {
            "color": "#ffffff !important"
        }
    }

    # JS: chọn ô đầu tiên, click ô thứ hai để hoán vị
    swap_cells_js = JsCode("""
    function(params) {
        if (!window.firstSelectedCell) {
            window.firstSelectedCell = {
                rowIndex: params.rowIndex,
                colId: params.column.colId,
                value: params.value,
                rowNode: params.node
            };
            params.api.refreshCells({force:true});
        } else {
            let cell1 = window.firstSelectedCell;
            let cell2_value = params.value;

            cell1.rowNode.setDataValue(cell1.colId, cell2_value);
            params.node.setDataValue(params.column.colId, cell1.value);

            window.firstSelectedCell = null;
            params.api.refreshCells({force:true});
        }
    }
    """)

    # JS: tô màu nền theo Thu/Tiet, chữ đỏ nếu trùng
    cell_style_js = JsCode("""
    function(params) {
        if (!params.data) return null;

        let thuVal = parseInt(params.data["Thu"]);
        let tietVal = parseInt(params.data["Tiet"]);
        let style = {};

        // nền theo Thu/Tiet
        if (!isNaN(thuVal) && !isNaN(tietVal)) {
            if (thuVal % 2 === 0) {
                style.backgroundColor = (tietVal <= 5) ? '#eeeeee' : '#cccccc';
            } else {
                style.backgroundColor = (tietVal <= 5) ? '#bbdefb' : '#90caf9';
            }
        }

        // nếu là cột Thu hoặc Tiet → chữ dark green
        if (params.column.colId === "Thu" || params.column.colId === "Tiet") {
            style.color = "darkblue";
            style.fontWeight = "900";
        }

        if (params.column.colId === "Tiet") {
            style.color = "darkblue";
            style.fontWeight = "700";
        }

        // highlight ô đang chọn để hoán vị
        if (window.firstSelectedCell && 
            window.firstSelectedCell.rowIndex === params.rowIndex && 
            window.firstSelectedCell.colId === params.column.colId) {
            style.backgroundColor = '#bbdefb';
            style.color = '#0d47a1';
            style.fontWeight = 'bold';
        }

        // kiểm tra trùng giá trị trong hàng
        let currentValue = params.value;
        if (currentValue !== "" && currentValue !== "nan") {
            let count = 0;
            for (let key in params.data) {
                if (key !== "Thu" && key !== "Tiet") {
                    if (params.data[key] === currentValue) {
                        count++;
                    }
                }
            }
            if (count > 1) {
                style.color = '#b71c1c'; // chữ đỏ cho ô trùng
                style.fontWeight = 'bold';
            }
        }

        return style;
    }
    """)

    gob = GridOptionsBuilder.from_dataframe(df)
    gob.configure_grid_options(onCellClicked=swap_cells_js)  # dùng click thay vì double-click
    gob.configure_default_column(
        cellStyle=cell_style_js,
        headerClass="my-blue-header",
        suppressMovable=True,
        resizable=False,
        width=80, minWidth=80, maxWidth=80
    )

    # cố định cột Thu và Tiet
    gob.configure_column("Thu", pinned="left", width=60, minWidth=60, maxWidth=60, headerClass="my-blue-header")
    gob.configure_column("Tiet", pinned="left", width=60, minWidth=60, maxWidth=60, headerClass="my-blue-header")

    grid_response = AgGrid(
        df,
        gridOptions=gob.build(),
        allow_unsafe_jscode=True,
        custom_css=custom_css,
        key="grid_timetable_final",
        update_mode="MODEL_CHANGED",
        reload_data=True
    )

    st.session_state.df = pd.DataFrame(grid_response["data"])

# --- Hàm popup dictionary ---
@st.dialog("Nội dung Dictionary", width="large")
def show_dict_popup(data_dict):
    df_small = pd.DataFrame(data_dict)
    gob_small = GridOptionsBuilder.from_dataframe(df_small)
    gob_small.configure_default_column(resizable=True, filter=True)
    AgGrid(df_small, gridOptions=gob_small.build(), height=200, key="small_grid_popup")
    #if st.button("Đóng"):
    #    st.rerun()

# --- Hàm menu chọn giáo viên ---
def show_teacher_menu(dfxet):
    # tap set cac gv
    gv_set = set()
    for col in dfxet.columns:
        if col not in ["Thu","Tiet"]:
            # loại bỏ NaN, bỏ hậu tố "_TT"
            values = dfxet[col].dropna().astype(str)
            clean_names = values.apply(lambda x: x.split("_")[0] if "_" in x else x)
            gv_set.update(clean_names.unique())

    print(gv_set)
    list_giao_viendsx = sorted(list(gv_set))

    selected_option = st.selectbox("👀 Xem tkb từng GV", options=["-- Xem TKB GV --"] + list_giao_viendsx, index=0)
    if selected_option != "-- Xem TKB GV --":
        sample_dict = build_teacher_schedule(dfxet, selected_option)
        show_dict_popup(sample_dict)

# --- Hàm nút lưu file ---
def save_button(): # dinh nghia ham save_button() co viec tao nut trong sidebar
    if st.sidebar.button("💾 Lưu file tkb cập nhật", type="primary", use_container_width=True, key='H1'):
        try:
            st.session_state.df.to_excel("Tkb_dang_dung/tkb_dang_dung.xlsx", index=False)
            st.success("🎉 Đã lưu tkb cập nhật thành công vào tệp: Tkb_dang_dung/tkb_dang_dung.xlsx")
        except Exception as e:
            st.error(f"Lỗi khi lưu file: {e}")

# --- Hàm nút lưu Xep lai TKB ---
def xeplaitkb_button():
    # neu click nut nay 
    if st.sidebar.button("⚙️ Xếp lại TKB", type="primary", use_container_width=True, key="H2"):
        # thi :
        try:
            #st.session_state.df.to_excel("Tkb_dang_dung/tkb_dang_dung.xlsx", index=False)
            st.success("🎉 Vua click nut xep lai TKB. Xin cho mot lat... ")
            xep_lai_tkb()
        except Exception as e:
            st.error(f"Lỗi khi xep: {e}")

# --- Main ---------------
if __name__ == "__main__":

    try:
        df_excel = pd.read_excel("tkb_dang_dung.xlsx")

        #st.session_state.df_excel = df_excel.astype(str).fillna("")
        st.session_state.df = df_excel.fillna("")

        # Lưu file âm thầm vào thư mục Tkb_da_dung trước khi sửa
        #df_excel.to_excel("Tkb_da_dung/tkb_dang_dung.xlsx", index=False)

        # Hiển thị bảng và các chức năng
        show_timetable(st.session_state.df)

        # tao 2 cot ben trai
        col1, col2 = st.columns(2)
        # cot 1 tao cac ham voi cac nut nhap
        with col1:
            save_button()
            xeplaitkb_button()
        # cot 2 tao ham tao ham show_teacher_menu(st.session_state.df)
        # chay ham voi tham so st.session_state.df
        with col2:
            show_teacher_menu(st.session_state.df)

    except FileNotFoundError: # neu chua co file ễcl thi yc upload file len
        uploaded_file = st.sidebar.file_uploader("📂 Chọn file Excel (.xlsx)", type=["xlsx"])
        if uploaded_file is not None:
            df_excel = pd.read_excel(uploaded_file)
            st.session_state.df = df_excel.fillna("")
            
            show_timetable(st.session_state.df)
            # tao 2 cot ben trai
            col1, col2 = st.columns(2)
            # cot 1 tao cac ham voi cac nut nhap
            with col1:
                save_button()
                xeplaitkb_button()
            # cot 2 tao ham tao ham show_teacher_menu(st.session_state.df)
            # chay ham voi tham so st.session_state.df
            with col2:
                show_teacher_menu(st.session_state.df)
