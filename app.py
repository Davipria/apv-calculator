import streamlit as st
import pandas as pd
import plotly.express as px
from apv_calculator import APVCalculator

def main():
    st.title("Calcolatore APV (Adjusted Present Value)")
    
    calculator = APVCalculator()
    
    # Inizializza session_state se non esiste
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = None
    
    # Aggiunta input per il ticker
    ticker = st.sidebar.text_input("Simbolo Azione (es. AAPL)", value="AAPL")
    
    if st.sidebar.button("Carica Dati"):
        try:
            with st.spinner("Caricamento dati finanziari..."):
                st.session_state.financial_data = calculator.get_financial_data(ticker)
                st.success(f"Dati caricati con successo per {ticker}")
                
                # Mostra i dati finanziari principali
                st.subheader("Dati Finanziari Principali")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Debito Totale", 
                             f"${st.session_state.financial_data['total_debt']:,.2f}")
                    st.metric("Aliquota Fiscale Effettiva", 
                             f"{st.session_state.financial_data['effective_tax_rate']*100:.2f}%")
                
                with col2:
                    st.metric("Flusso di Cassa Operativo (Ultimo Anno)", 
                             f"${st.session_state.financial_data['operating_cashflow'][0]:,.2f}")
        except Exception as e:
            st.error(f"Errore nel caricamento dei dati: {str(e)}")
    
    # Sidebar per input
    st.sidebar.header("Parametri di Input")
    
    # Input per i flussi di cassa
    st.sidebar.subheader("Flussi di Cassa")
    if st.session_state.financial_data is not None:
        cash_flows = st.session_state.financial_data['operating_cashflow'][:5]  # Ultimi 5 anni
        num_years = len(cash_flows)
    else:
        num_years = st.sidebar.number_input("Numero di anni", min_value=1, max_value=10, value=5)
        cash_flows = []
        for i in range(num_years):
            cf = st.sidebar.number_input(f"Flusso di cassa anno {i+1}", value=1000.0)
            cash_flows.append(cf)
    
    # Altri parametri
    if st.session_state.financial_data is not None:
        tax_rate = st.sidebar.number_input("Aliquota fiscale (%)", 
                                         value=float(st.session_state.financial_data['effective_tax_rate']*100),
                                         min_value=0.0, max_value=100.0) / 100
        debt = st.session_state.financial_data['total_debt']
    else:
        tax_rate = st.sidebar.number_input("Aliquota fiscale (%)", 
                                         value=25.0, min_value=0.0, max_value=100.0) / 100
        debt = st.sidebar.number_input("Debito", min_value=0.0, value=1000.0)
    
    discount_rate = st.sidebar.number_input("Tasso di sconto (%)", 
                                          min_value=0.0, max_value=100.0, value=10.0) / 100
    cost_of_debt = st.sidebar.number_input("Costo del debito (%)", 
                                         min_value=0.0, max_value=100.0, value=5.0) / 100
    
    # Calcoli
    npv = calculator.calculate_npv(cash_flows, discount_rate)
    tax_shield = calculator.calculate_tax_shield(debt, tax_rate, cost_of_debt)
    apv = calculator.calculate_apv(npv, tax_shield)
    
    # Visualizzazione risultati dettagliati
    st.header("Risultati Dettagliati")
    
    # Mostra i flussi di cassa utilizzati
    st.subheader("Flussi di Cassa Utilizzati")
    df_cashflows = pd.DataFrame({
        'Anno': [f'Anno {i+1}' for i in range(len(cash_flows))],
        'Flusso di Cassa ($)': cash_flows
    })
    st.dataframe(df_cashflows.style.format({'Flusso di Cassa ($)': '${:,.2f}'}))
    
    # Mostra i parametri utilizzati
    st.subheader("Parametri Utilizzati")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tasso di Sconto", f"{discount_rate*100:.2f}%")
    with col2:
        st.metric("Costo del Debito", f"{cost_of_debt*100:.2f}%")
    with col3:
        st.metric("Aliquota Fiscale", f"{tax_rate*100:.2f}%")
    
    # Mostra i risultati dei calcoli
    st.subheader("Risultati dei Calcoli")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "NPV (Valore Attuale Netto)", 
            f"${npv:,.2f}",
            help="Valore attuale dei flussi di cassa futuri scontati"
        )
    with col2:
        st.metric(
            "Benefici Fiscali", 
            f"${tax_shield:,.2f}",
            help="Valore attuale dei benefici fiscali del debito"
        )
    with col3:
        st.metric(
            "APV (Adjusted Present Value)", 
            f"${apv:,.2f}",
            help="Somma del NPV e dei benefici fiscali"
        )
    
    # Mostra il dettaglio dei calcoli
    st.subheader("Dettaglio dei Calcoli")
    with st.expander("Mostra dettaglio calcoli"):
        st.write("**Formula NPV:**")
        st.latex(r"NPV = \sum_{t=1}^{n} \frac{CF_t}{(1 + r)^t}")
        st.write("Dove:")
        st.write("- CF_t = Flusso di cassa al tempo t")
        st.write("- r = Tasso di sconto")
        st.write("- n = Numero di periodi")
        
        st.write("\n**Formula Tax Shield:**")
        st.latex(r"TS = D \times \tau \times (1 - \frac{1}{1 + r_d})")
        st.write("Dove:")
        st.write("- D = Debito totale")
        st.write("- τ = Aliquota fiscale")
        st.write("- r_d = Costo del debito")
        
        st.write("\n**Formula APV:**")
        st.latex(r"APV = NPV + TS")
    
    # Mostra i dati di input
    if st.session_state.financial_data is not None:
        st.subheader("Dati Finanziari Utilizzati")
        with st.expander("Mostra dati finanziari"):
            st.write("**Debito Totale:**", f"${st.session_state.financial_data['total_debt']:,.2f}")
            st.write("**Aliquota Fiscale Effettiva:**", 
                    f"{st.session_state.financial_data['effective_tax_rate']*100:.2f}%")
            st.write("\n**Flussi di Cassa Operativi:**")
            st.dataframe(pd.DataFrame(st.session_state.financial_data['operating_cashflow'], 
                                    columns=['Valore ($)']).style.format({'Valore ($)': '${:,.2f}'}))
    
    # Analisi di sensibilità
    st.header("Analisi di Sensibilità")
    variations = [-0.2, -0.1, 0, 0.1, 0.2]
    sensitivity = calculator.sensitivity_analysis(apv, variations)
    
    df_sensitivity = pd.DataFrame({
        'Variazione': [f"{v*100}%" for v in sensitivity['variations']],
        'APV': sensitivity['values']
    })
    
    fig = px.line(df_sensitivity, x='Variazione', y='APV', 
                  title='Analisi di Sensibilità APV')
    st.plotly_chart(fig)
    
    # Mostra i dati storici se disponibili
    if st.session_state.financial_data is not None:
        st.header("Dati Storici")
        
        tab1, tab2, tab3 = st.tabs(["Flussi di Cassa", "Bilancio", "Conto Economico"])
        
        with tab1:
            st.dataframe(st.session_state.financial_data['cashflow'])
        with tab2:
            st.dataframe(st.session_state.financial_data['balance_sheet'])
        with tab3:
            st.dataframe(st.session_state.financial_data['income_stmt'])

if __name__ == "__main__":
    main() 