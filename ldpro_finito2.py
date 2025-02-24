import itertools
from typing import Optional, Dict, List, Union

class ValidatoreProposizione:
    """Classe per la validazione e manipolazione di proposizioni logiche."""
    
    OPERATORI = {"NOT", "AND", "OR", "=>", "<=>", "^", "V", "-|"}
    RAPPRESENTAZIONE_LEGGIBILE = {
        'NOT': 'NOT',
        'AND': 'AND',
        'OR': 'OR',
        '=>': 'IMPLICA',
        '<=>': 'EQUIVALE',
        '^': 'AND',
        'V': 'OR',
        '-|': 'NOT'
    }

    def valida_stringa(self, proposizione: str) -> None:
        """Verifica che la stringa della proposizione sia sintatticamente valida."""
        
        bilanciamento = 0
        caratteri_validi = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz()_ ') | self.OPERATORI
        carattere_precedente = None
        token_list = [token.strip() for token in proposizione.split("_") if token.strip()]

        for idx, token in enumerate(token_list):
            if token not in caratteri_validi and token not in {"=>", "<=>"}:  # Gestione speciale per operatori multi-carattere
                raise ValueError(f"Carattere non valido trovato in: '{token}' alla posizione {idx}.")

            if token == "(":
                bilanciamento += 1
                if carattere_precedente and carattere_precedente not in self.OPERATORI and carattere_precedente != "(":
                    raise ValueError(f"Operando mancante dopo '(' alla posizione {idx}.")

            elif token == ")":
                bilanciamento -= 1
                if bilanciamento < 0:
                    raise ValueError(f"Parentesi chiusa senza apertura corrispondente alla posizione {idx}.")
                if carattere_precedente in self.OPERATORI:
                    raise ValueError(f"Operatore '{carattere_precedente}' non seguito da operando prima di ')' alla posizione {idx}.")

            elif token in self.OPERATORI:
                if token not in {"NOT", "-|"}:
                    if carattere_precedente is None or (carattere_precedente in self.OPERATORI and carattere_precedente not in {"NOT", "-|"}) or carattere_precedente == "(":
                        raise ValueError(f"Operatore '{token}' posizionato in modo errato alla posizione {idx}.")
                else:
                    if carattere_precedente and not (carattere_precedente in self.OPERATORI or carattere_precedente == "("):
                        raise ValueError(f"Operatore '{token}' posizionato in modo errato alla posizione {idx}.")

            else:
                if carattere_precedente and (carattere_precedente not in self.OPERATORI and carattere_precedente != "("):
                    raise ValueError(f"Operatore mancante tra operandi alla posizione {idx}.")

            if token == ")" and carattere_precedente == "(":
                raise ValueError(f"Parentesi vuote rilevate alla posizione {idx-1} e {idx}.")

            carattere_precedente = token

        if bilanciamento != 0:
            raise ValueError("Parentesi non bilanciate nella proposizione logica.")

        if carattere_precedente in {"AND", "OR", "=>", "<=>", "^", "V"}:
            raise ValueError(f"Proposizione termina con l'operatore '{carattere_precedente}', che richiede un operando.")

    def in_formato_leggibile(self, proposizione: str) -> str:
        """Converte la proposizione in una forma leggibile."""
        token_list = proposizione.split("_")
        return " ".join(self.RAPPRESENTAZIONE_LEGGIBILE.get(token.strip(), token.strip()) 
                       for token in token_list if token.strip())

class Nodo:
    """Rappresenta un nodo nell'albero sintattico di una proposizione logica."""
    
    def __init__(self, valore: str):
        self.valore: Union[str, bool] = valore
        self.sinistra: Optional[Nodo] = None
        self.destra: Optional[Nodo] = None

    def assegna(self, d: Dict[str, bool]) -> None:
        """Assegna ricorsivamente valori booleani alle variabili."""
        if self.sinistra is not None:
            self.sinistra.assegna(d)
        if self.destra is not None:
            self.destra.assegna(d)
        if isinstance(self.valore, str) and self.valore in d:
            self.valore = d[self.valore]

    def valuta(self) -> bool:
        """Valuta ricorsivamente l'albero della proposizione."""
        if not isinstance(self.valore, str) or self.valore not in ValidatoreProposizione.OPERATORI:
            return bool(self.valore)
        if self.valore in {"NOT", "-|"}:
            return not self.sinistra.valuta()
        val_sinistra = self.sinistra.valuta() if self.sinistra else False
        val_destra = self.destra.valuta() if self.destra else False
        if self.valore in {"AND", "^"}:
            return val_sinistra and val_destra
        elif self.valore in {"OR", "V"}:
            return val_sinistra or val_destra
        elif self.valore == "=>":
            return (not val_sinistra) or val_destra
        elif self.valore == "<=>":
            return val_sinistra == val_destra
        return False

    def clona(self) -> 'Nodo':
        """Crea una copia profonda del nodo e del suo sottoalbero."""
        nuovo_nodo = Nodo(self.valore)
        if self.sinistra:
            nuovo_nodo.sinistra = self.sinistra.clona()
        if self.destra:
            nuovo_nodo.destra = self.destra.clona()
        return nuovo_nodo

    def __str__(self, livello: int = 0) -> str:
        """Fornisce una rappresentazione testuale dell'albero."""
        ret = "    " * livello + str(self.valore) + "\n"
        if self.sinistra:
            ret += self.sinistra.__str__(livello + 1)
        if self.destra:
            ret += self.destra.__str__(livello + 1)
        return ret

def costruisci_albero_validato(s: str) -> Nodo:
    """Costruisce un albero sintattico dopo aver validato la stringa."""
    validatore = ValidatoreProposizione()
    validatore.valida_stringa(s)
    return costruisci_albero(s)

def costruisci_albero(s: str) -> Nodo:
    """Costruisce ricorsivamente un albero della proposizione."""
    token_list = [token.strip() for token in s.split("_") if token.strip() != '']
    pila_operatori: List[str] = []
    pila_operandi: List[Union[Nodo, str]] = []
    
    for token in token_list:
        if token == "(":
            continue
        elif token in ValidatoreProposizione.OPERATORI:
            pila_operatori.append(token)
        elif token == ")":
            if not pila_operatori:
                raise ValueError("Parentesi non bilanciate")
            op = pila_operatori.pop()
            if op in {"NOT", "-|"}:
                if not pila_operandi:
                    raise ValueError(f"Operando mancante per {op}")
                operando = pila_operandi.pop()
                nodo = Nodo(op)
                nodo.sinistra = operando if isinstance(operando, Nodo) else Nodo(operando)
            else:
                if len(pila_operandi) < 2:
                    raise ValueError(f"Operandi insufficienti per {op}")
                destra = pila_operandi.pop()
                sinistra = pila_operandi.pop()
                nodo = Nodo(op)
                nodo.sinistra = sinistra if isinstance(sinistra, Nodo) else Nodo(sinistra)
                nodo.destra = destra if isinstance(destra, Nodo) else Nodo(destra)
            pila_operandi.append(nodo)
        else:
            pila_operandi.append(token)
    
    if len(pila_operandi) != 1:
        raise ValueError("Espressione malformata")
    
    return pila_operandi.pop()

def estrai_variabili(s: str) -> List[str]:
    """Estrae le variabili dalla stringa dell'espressione."""
    token_list = [token.strip() for token in s.split("_") if token.strip() != '']
    return sorted(list({token for token in token_list 
                       if token not in ValidatoreProposizione.OPERATORI and token not in {"(", ")"}}))

def calcola_TdV(albero: Nodo, variabili: List[str]) -> List[List[Union[str, bool]]]:
    """Calcola la tabella di verità per una proposizione."""
    intestazione = variabili + ["Proposizione"]
    tabella_verita = [intestazione]
    for assegnazione in itertools.product([False, True], repeat=len(variabili)):
        dizionario_assegnazione = dict(zip(variabili, assegnazione))
        albero_copia = albero.clona()
        albero_copia.assegna(dizionario_assegnazione)
        risultato = albero_copia.valuta()
        tabella_verita.append(list(assegnazione) + [risultato])
    return tabella_verita

def crea_dnf(tabella_verita: List[List[Union[str, bool]]], variabili: List[str]) -> str:
    """Genera la forma normale disgiuntiva."""
    clausole = []
    for riga in tabella_verita[1:]:
        if riga[-1]:  # Se il risultato è True
            letterali = []
            for var, val in zip(variabili, riga[:-1]):
                letterali.append(var if val else f"NOT_{var}")
            clausole.append("(" + " AND ".join(letterali) + ")")
    return " OR ".join(clausole) if clausole else "False"

def crea_cnf(tabella_verita: List[List[Union[str, bool]]], variabili: List[str]) -> str:
    """Genera la forma normale congiuntiva."""
    clausole = []
    for riga in tabella_verita[1:]:
        if not riga[-1]:  # Se il risultato è False
            letterali = []
            for var, val in zip(variabili, riga[:-1]):
                letterali.append(f"NOT_{var}" if val else var)
            clausole.append("(" + " OR ".join(letterali) + ")")
    return " AND ".join(clausole) if clausole else "True"

def tautologia(tabella_verita: List[List[Union[str, bool]]]) -> bool:
    """Verifica se la proposizione è una tautologia."""
    return all(riga[-1] for riga in tabella_verita[1:])

def soddisfacibile(tabella_verita: List[List[Union[str, bool]]]) -> bool:
    """Verifica se la proposizione è soddisfacibile."""
    return any(riga[-1] for riga in tabella_verita[1:])

def insoddisfacibile(tabella_verita: List[List[Union[str, bool]]]) -> bool:
    """Verifica se la proposizione è insoddisfacibile."""
    return not soddisfacibile(tabella_verita)

def falsificabile(tabella_verita: List[List[Union[str, bool]]]) -> bool:
    """Verifica se la proposizione è falsificabile."""
    return any(not riga[-1] for riga in tabella_verita[1:])

def equivalenza(albero1: Nodo, albero2: Nodo) -> bool:
    """Verifica l'equivalenza logica tra due proposizioni."""
    if not isinstance(albero1, Nodo) or not isinstance(albero2, Nodo):
        raise TypeError("Gli argomenti devono essere istanze di Nodo")

    def estrai_variabili_da_albero(nodo: Nodo, variabili: set) -> None:
        if isinstance(nodo.valore, str):
            if nodo.valore not in ValidatoreProposizione.OPERATORI and nodo.valore not in {"(", ")"}:
                variabili.add(nodo.valore)
        if nodo.sinistra:
            estrai_variabili_da_albero(nodo.sinistra, variabili)
        if nodo.destra:
            estrai_variabili_da_albero(nodo.destra, variabili)

    tutte_variabili = set()
    estrai_variabili_da_albero(albero1, tutte_variabili)
    estrai_variabili_da_albero(albero2, tutte_variabili)
    variabili_ordinate = sorted(list(tutte_variabili))

    for valori in itertools.product([False, True], repeat=len(variabili_ordinate)):
        assegnazione = dict(zip(variabili_ordinate, valori))
        albero1_copia = albero1.clona()
        albero2_copia = albero2.clona()
        albero1_copia.assegna(assegnazione)
        albero2_copia.assegna(assegnazione)
        if albero1_copia.valuta() != albero2_copia.valuta():
            return False
    return True

def stampa_TdV(tabella_verita: List[List[Union[str, bool]]]) -> None:
    """Stampa la tabella di verità in formato tabellare."""
    larghezze = [max(len(str(riga[i])) for riga in tabella_verita) 
                 for i in range(len(tabella_verita[0]))]
    
    intestazione = tabella_verita[0]
    linea_intestazione = " | ".join(str(val).ljust(larghezze[i]) 
                                  for i, val in enumerate(intestazione))
    separatore = "-+-".join('-' * larghezze[i] for i in range(len(larghezze)))
    
    print(linea_intestazione)
    print(separatore)
    
    for riga in tabella_verita[1:]:
        linea = " | ".join(str(val).ljust(larghezze[i]) for i, val in enumerate(riga))
        print(linea)

if __name__ == "__main__":
    # Test del modulo
    espressione1 = "( _ ( _ ( _ a _ => _ c _ ) _ AND _ ( _ b _ => _ c _ ) _ ) _ <=> _ ( _ ( _ a _ OR _ b _ ) _ => _ c _ ) _ )"
    espressione2 = "( _ ( _ a _ AND _ c _ ) _ OR _ ( _ b _ => _ c _ ) _ )"
    
    try:
        # Analisi della prima proposizione
        albero1 = costruisci_albero_validato(espressione1)
        variabili1 = estrai_variabili(espressione1)
        tabella1 = calcola_TdV(albero1, variabili1)
        
        print("Albero della prima proposizione:")
        print(albero1)
        print("\nTabella di Verità:")
        stampa_TdV(tabella1)
        
        print("\nProprietà della proposizione:")
        print("Tautologia?:", tautologia(tabella1))
        print("Soddisfacibile?:", soddisfacibile(tabella1))
        print("Insoddisfacibile?:", insoddisfacibile(tabella1))
        print("Falsificabile?:", falsificabile(tabella1))
        
        print("\nForme Normali:")
        print("DNF:", crea_dnf(tabella1, variabili1))
        print("CNF:", crea_cnf(tabella1, variabili1))
        
        # Test di equivalenza
        albero2 = costruisci_albero_validato(espressione2)
        print("\nEquivalenza tra le proposizioni:", equivalenza(albero1, albero2))
        
    except ValueError as errore:
        print("Errore:", errore)

    # Test con espressioni non valide
    print("\n=== Test di validazione espressioni non valide ===")

    # Test con parentesi vuote consecutive
    try:
        print("\nTest con espressione non valida '( _ ) _ ( _ ) _ ( _ p _ q _ )':")
        invalid_proposition = costruisci_albero_validato("( _ q _ => _ ( _ NOT _ r _ ) _ )")
    except ValueError as ve:
        print("Errore:", ve)

    # Test con espressione senza operatori tra atomi
    try:
        print("\nTest con espressione non valida '( _ p _ q _ p _ )':")
        invalid_proposition2 = costruisci_albero_validato("( _ p _ q _ p _ )")
    except ValueError as ve:
        print("Errore:", ve)

    # Test con operatore isolato
    try:
        print("\nTest con espressione non valida '( _ AND _ p _ q _ )':")
        invalid_proposition3 = costruisci_albero_validato("( _ AND _ p _ q _ )")
    except ValueError as ve:
        print("Errore:", ve)

    # Test con operatore all'inizio
    try:
        print("\nTest con espressione non valida 'AND _ ( _ p _ q _ )':")
        invalid_proposition4 = costruisci_albero_validato("AND _ ( _ p _ AND _ q _ )")
    except ValueError as ve:
        print("Errore:", ve)

    # Test con parentesi non bilanciate
    try:
        print("\nTest con espressione non valida '( _ ( _ p _ AND _ q _ )':")
        invalid_proposition5 = costruisci_albero_validato("( _ ( _ p _ AND _ q _ )")
    except ValueError as ve:
        print("Errore:", ve)
    