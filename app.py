import streamlit as st
import pandas as pd
import os

# 웹사이트 전체 화면 넓게 쓰기 설정
st.set_page_config(page_title="오륜중학교 아침축구리그", page_icon="⚽", layout="wide")

st.title("⚽ 오륜중학교 아침축구리그")

# --- 파일 경로 설정 ---
TEAMS_FILE = "teams_data.csv"
PLAYERS_FILE = "players_data.csv"

# --- 데이터 불러오기 및 초기화 함수 ---
def load_data():
    # 1. 팀 데이터 로드
    if os.path.exists(TEAMS_FILE):
        teams_df = pd.read_csv(TEAMS_FILE)
    else:
        teams_df = pd.DataFrame({
            '팀명': ['A팀', 'B팀', 'C팀'],
            '승': [0, 0, 0],
            '무': [0, 0, 0],
            '패': [0, 0, 0],
            '득점': [0, 0, 0],
            '실점': [0, 0, 0]
        })
        teams_df.to_csv(TEAMS_FILE, index=False)
        
    # 2. 선수 데이터 로드
    if os.path.exists(PLAYERS_FILE):
        players_df = pd.read_csv(PLAYERS_FILE)
    else:
        players_df = pd.DataFrame(
            columns=['이름', '소속팀', '포지션', '등번호', '골', '도움', '포인트']
        )
        players_df.to_csv(PLAYERS_FILE, index=False)
        
    return teams_df, players_df

# 데이터 세팅
df_teams, df_players = load_data()

# --- 탭(메뉴) 만들기 ---
tab1, tab2, tab3 = st.tabs(["📊 팀 순위표", "🏃‍♂️ 개인 랭킹", "⚙️ 관리자 설정 (기록 입력)"])

# --- TAB 1: 팀 순위표 ---
with tab1:
    st.header("🏆 현재 팀 순위")
    
    t_df = df_teams.copy()
    t_df['승점'] = (t_df['승'] * 3) + (t_df['무'] * 1)
    t_df['득실차'] = t_df['득점'] - t_df['실점']
    
    t_df = t_df.sort_values(
        by=['승점', '득실차', '득점'], 
        ascending=[False, False, False]
    ).reset_index(drop=True)
    
    t_df.index = t_df.index + 1  
    
    display_teams = t_df[['팀명', '승점', '승', '무', '패', '득점', '실점', '득실차']]
    st.dataframe(display_teams, use_container_width=True)

# --- TAB 2: 개인 랭킹 (득점, 도움, 포인트) ---
with tab2:
    st.header("🔥 선수 개인 기록 및 랭킹")
    
    if len(df_players) == 0:
        st.info("아직 등록된 선수가 없습니다. 관리자 탭에서 선수를 추가해주세요.")
    else:
        p_df = df_players.copy()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("⚽ 득점왕 랭킹")
            top_scorers = p_df.sort_values(by='골', ascending=False)[['이름', '소속팀', '골']].head(5)
            top_scorers = top_scorers[top_scorers['골'] > 0].reset_index(drop=True)
            top_scorers.index = top_scorers.index + 1
            st.dataframe(top_scorers, use_container_width=True)
            
        with col2:
            st.subheader("👟 도움왕 랭킹")
            top_assists = p_df.sort_values(by='도움', ascending=False)[['이름', '소속팀', '도움']].head(5)
            top_assists = top_assists[top_assists['도움'] > 0].reset_index(drop=True)
            top_assists.index = top_assists.index + 1
            st.dataframe(top_assists, use_container_width=True)
            
        with col3:
            st.subheader("🌟 포인트 랭킹 (골+도움)")
            top_points = p_df.sort_values(by='포인트', ascending=False)[['이름', '소속팀', '포인트']].head(5)
            top_points = top_points[top_points['포인트'] > 0].reset_index(drop=True)
            top_points.index = top_points.index + 1
            st.dataframe(top_points, use_container_width=True)
        
        st.divider()
        st.subheader("전체 선수 명단")
        st.dataframe(p_df.sort_values(by='포인트', ascending=False).reset_index(drop=True), use_container_width=True)

# --- TAB 3: 관리자 설정 (비밀번호 잠금 적용) ---
with tab3:
    st.header("⚙️ 관리자 설정 및 기록 입력")
    
    password_input = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    if password_input == "OMS26":
        st.success("🔒 관리자 권한이 확인되었습니다!")
        st.divider()
        
        # 팀 이름 변경하기
        st.subheader("✏️ 팀 이름 변경하기")
        target_team = st.selectbox("이름을 바꿀 팀 선택", df_teams['팀명'].tolist(), key="rename_target")
        new_team_name = st.text_input("새로운 팀 이름 입력")
        
        if st.button("팀 이름 변경 적용"):
            if new_team_name and new_team_name not in df_teams['팀명'].tolist():
                team_idx = df_teams[df_teams['팀명'] == target_team].index[0]
                df_teams.at[team_idx, '팀명'] = new_team_name
                
                if len(df_players) > 0:
                    df_players.loc[df_players['소속팀'] == target_team, '소속팀'] = new_team_name
                
                # 파일에 저장
                df_teams.to_csv(TEAMS_FILE, index=False)
                df_players.to_csv(PLAYERS_FILE, index=False)
                
                st.success(f"팀 이름이 '{target_team}'에서 '{new_team_name}'(으)로 변경되었습니다!")
                st.rerun()
            else:
                st.error("이미 존재하는 팀명이거나 올바른 이름을 입력해주세요.")
                
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ 신규 선수 등록")
            with st.form("add_player_form"):
                new_name = st.text_input("선수 이름")
                new_team = st.selectbox("소속팀", df_teams['팀명'].tolist())
                new_position = st.selectbox("포지션", ["FW (공격수)", "MF (미드필더)", "DF (수비수)", "GK (골키퍼)"])
                new_number = st.number_input("등번호", min_value=1, max_value=99, step=1)
                
                submit_player = st.form_submit_button("선수 등록하기")
                
                if submit_player and new_name:
                    new_row = pd.DataFrame([{
                        '이름': new_name, '소속팀': new_team, '포지션': new_position, 
                        '등번호': new_number, '골': 0, '도움': 0, '포인트': 0
                    }])
                    df_players = pd.concat([df_players, new_row], ignore_index=True)
                    
                    # 파일에 저장
                    df_players.to_csv(PLAYERS_FILE, index=False)
                    
                    st.success(f"{new_name} 선수가 등록되었습니다!")
                    st.rerun()

        with col2:
            st.subheader("📈 경기 결과 및 스탯 업데이트")
            
            # 1. 팀 결과 업데이트
            st.write("**팀 경기 결과 입력**")
            update_team = st.selectbox("결과를 입력할 팀 선택", df_teams['팀명'].tolist(), key="result_team")
            match_result = st.radio("경기 결과", ["승리", "무승부", "패배"], horizontal=True)
            scored_goals = st.number_input("해당 경기 득점 수", min_value=0, step=1, key="match_scored")
            conceded_goals = st.number_input("해당 경기 실점 수", min_value=0, step=1, key="match_conceded")
            
            if st.button("팀 결과 적용"):
                idx = df_teams[df_teams['팀명'] == update_team].index[0]
                
                if match_result == "승리":
                    df_teams.at[idx, '승'] += 1
                elif match_result == "무승부":
                    df_teams.at[idx, '무'] += 1
                else:
                    df_teams.at[idx, '패'] += 1
                
                df_teams.at[idx, '득점'] += scored_goals
                df_teams.at[idx, '실점'] += conceded_goals
                
                # 파일에 저장
                df_teams.to_csv(TEAMS_FILE, index=False)
                
                st.success("팀 경기 결과가 업데이트 되었습니다!")
                st.rerun()
                
            st.divider()
            
            # 2. 선수 스탯 업데이트
            st.write("**개인 스탯 추가 (골/도움)**")
            if len(df_players) > 0:
                update_player = st.selectbox("스탯을 추가할 선수 선택", df_players['이름'].tolist())
                add_goal = st.number_input("추가할 골 수", min_value=0, step=1, key="player_goal")
                add_assist = st.number_input("추가할 도움 수", min_value=0, step=1, key="player_assist")
                
                if st.button("스탯 적용"):
                    idx = df_players[df_players['이름'] == update_player].index[0]
                    df_players.at[idx, '골'] += add_goal
                    df_players.at[idx, '도움'] += add_assist
                    df_players.at[idx, '포인트'] = df_players.at[idx, '골'] + df_players.at[idx, '도움']
                    
                    # 파일에 저장
                    df_players.to_csv(PLAYERS_FILE, index=False)
                    
                    st.success("개인 스탯이 업데이트 되었습니다!")
                    st.rerun()
            else:
                st.warning("먼저 선수를 등록해주세요.")
                
    elif password_input == "":
        st.info("관리자 기능을 이용하려면 비밀번호를 입력하세요.")
    else:
        st.error("❌ 비밀번호가 틀렸습니다. 올바른 비밀번호를 입력해주세요.")