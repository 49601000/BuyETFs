# 値が存在し、数値かどうかチェックしてから表示
if latest is not None:
    close_val = latest.get('Close', None)
    rsi_val = latest.get('RSI', None)
    ma200_val = latest.get('MA200', None)

    if isinstance(close_val, (int, float)) and pd.notna(close_val):
        st.write(f"💰 **現在の価格**: {close_val:.2f} USD")
    else:
        st.warning("現在価格が有効な数値ではありません。")

    if isinstance(rsi_val, (int, float)) and pd.notna(rsi_val):
        st.write(f"📊 **RSI (14日)**: {rsi_val:.2f}")
    else:
        st.warning("RSIが有効な数値ではありません。")

    if isinstance(ma200_val, (int, float)) and pd.notna(ma200_val):
        st.write(f"📉 **200日移動平均**: {ma200_val:.2f}")
    else:
        st.warning("200日移動平均が有効な数値ではありません。")
        
