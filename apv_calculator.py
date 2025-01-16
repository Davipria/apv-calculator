import numpy as np
import pandas as pd
import yfinance as yf
from typing import List, Dict, Union

class APVCalculator:
    def __init__(self):
        self.results = {}
    
    def calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """
        Calcola il Valore Attuale Netto dei flussi di cassa
        
        Args:
            cash_flows: Lista dei flussi di cassa futuri
            discount_rate: Tasso di sconto (es. 0.10 per 10%)
        """
        # Converti i cash flows in numeri positivi e rimuovi eventuali None o nan
        clean_cash_flows = []
        for cf in cash_flows:
            if cf is not None and not pd.isna(cf):
                clean_cash_flows.append(abs(float(cf)))
        
        # Verifica che ci siano flussi di cassa validi
        if not clean_cash_flows:
            return 0.0
        
        npv = 0.0
        for t, cf in enumerate(clean_cash_flows):
            npv += cf / ((1 + discount_rate) ** (t + 1))
        
        return npv
    
    def calculate_tax_shield(self, debt: float, tax_rate: float, cost_of_debt: float) -> float:
        """
        Calcola il valore attuale dei benefici fiscali del debito
        
        Args:
            debt: Valore del debito
            tax_rate: Aliquota fiscale (es. 0.25 per 25%)
            cost_of_debt: Costo del debito (es. 0.05 per 5%)
        """
        # Verifica che i valori siano validi
        if debt is None or tax_rate is None or cost_of_debt is None:
            return 0.0
        
        if cost_of_debt == 0:  # Evita la divisione per zero
            return debt * tax_rate
        
        return float(debt) * float(tax_rate) * (1 - 1/(1 + float(cost_of_debt)))
    
    def calculate_apv(self, npv: float, tax_shield: float) -> float:
        """
        Calcola l'Adjusted Present Value
        """
        return npv + tax_shield
    
    def sensitivity_analysis(self, base_value: float, 
                           variations: List[float]) -> Dict[str, List[float]]:
        """
        Esegue l'analisi di sensibilità sul valore base
        
        Args:
            base_value: Valore base per l'analisi
            variations: Lista delle variazioni percentuali (es. [-0.1, 0, 0.1])
        """
        results = {
            'variations': variations,
            'values': [base_value * (1 + v) for v in variations]
        }
        return results
    
    def get_financial_data(self, ticker: str) -> Dict[str, Union[pd.DataFrame, float]]:
        """
        Recupera i dati finanziari dettagliati usando Yahoo Finance
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Ottieni il bilancio e il conto economico
            balance_sheet = stock.balance_sheet
            income_stmt = stock.financials
            cashflow = stock.cashflow
            
            # Calcola i flussi di cassa operativi (ultimi 4 anni)
            if 'Operating Cash Flow' in cashflow.index:
                operating_cashflow = cashflow.loc['Operating Cash Flow'].values
            elif 'Total Cash From Operating Activities' in cashflow.index:
                operating_cashflow = cashflow.loc['Total Cash From Operating Activities'].values
            else:
                operating_cashflow = np.zeros(4)  # Default a zero se non trovato
            
            # Ottieni il debito totale dall'ultimo anno
            debt_labels = ['Total Debt', 'Long Term Debt', 'Total Long Term Debt']
            total_debt = 0
            for label in debt_labels:
                if label in balance_sheet.index:
                    total_debt = float(balance_sheet.loc[label].iloc[0])
                    break
            
            # Calcola l'aliquota fiscale effettiva dall'ultimo anno
            if 'Income Tax Expense' in income_stmt.index and 'Pretax Income' in income_stmt.index:
                tax_expense = float(income_stmt.loc['Income Tax Expense'].iloc[0])
                pretax_income = float(income_stmt.loc['Pretax Income'].iloc[0])
                effective_tax_rate = tax_expense / pretax_income if pretax_income != 0 else 0.25
            else:
                effective_tax_rate = 0.25  # Valore di default
            
            return {
                'operating_cashflow': operating_cashflow.tolist(),
                'total_debt': total_debt,
                'effective_tax_rate': effective_tax_rate,
                'balance_sheet': balance_sheet,
                'income_stmt': income_stmt,
                'cashflow': cashflow
            }
            
        except Exception as e:
            print(f"Dettaglio errore: {e}")  # Per debug
            raise Exception(f"Errore nel recupero dei dati per {ticker}: {str(e)}") 