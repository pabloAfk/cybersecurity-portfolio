#!/usr/bin/env python3
"""
SISTEMA DE CRIPTOGRAFIA HOMOFÔNICA - VERSÃO PYTHON
Portado do script Bash original
Mantém compatibilidade total com a versão Bash
"""

import random
import re
from typing import Dict, Tuple, List

# ========== CONSTANTES ==========
POOL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .()\"!?"

# Mapeamento de normalização de caracteres acentuados e especiais
NORMALIZACAO = {
    # Vogais minúsculas acentuadas
    'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
    'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
    'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
    # Vogais maiúsculas acentuadas
    'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
    'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
    'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
    'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
    'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
    # Cedilha
    'ç': 'c', 'Ç': 'C',
    # Pontuação
    ',': '.', ';': '.', ':': '.',
    '-': ' ', '_': ' ',
}


def normalizar_caractere(char: str) -> str:
    """
    Normaliza caracteres acentuados e especiais para o conjunto CHARS
    """
    if char in CHARS:
        return char
    
    if char in NORMALIZACAO:
        return NORMALIZACAO[char]
    
    # Qualquer outro caractere vira espaço
    return ' '


def gerar_mapa(key1: int) -> Dict[str, str]:
    """
    Gera mapa de substituição homofônico sem colisões
    Cada caractere do CHARS recebe uma representação única de 5 caracteres do POOL
    
    Args:
        key1: Chave primária (0-999)
    
    Returns:
        Dicionário mapeando caractere -> representação de 5 chars
    """
    usados = set()
    mapa = {}
    
    for i, char in enumerate(CHARS):
        tentativa = 0
        
        while True:
            seed = key1 * (i + 1) * 12345 + tentativa * 9999
            repr_chars = []
            
            for j in range(5):
                idx = (seed + j * 1000) % len(POOL)
                repr_chars.append(POOL[idx])
            
            representacao = ''.join(repr_chars)
            
            # Verifica se já foi usado
            if representacao not in usados:
                usados.add(representacao)
                mapa[char] = representacao
                break
            
            tentativa += 1
            
            # Segurança: se tentar muitas vezes, muda estratégia
            if tentativa > 100:
                # Usa posição direta no pool
                repr_chars = []
                for j in range(5):
                    idx = (i * 1000 + j + tentativa) % len(POOL)
                    repr_chars.append(POOL[idx])
                representacao = ''.join(repr_chars)
                
                if representacao not in usados:
                    usados.add(representacao)
                    mapa[char] = representacao
                    break
                tentativa += 1
    
    return mapa


def calcular_rotacao(key2: int, pos: int) -> int:
    """
    Calcula o número de posições para rotação baseado na chave secundária e posição
    
    Args:
        key2: Chave secundária (0-999)
        pos: Posição do caractere no texto
    
    Returns:
        Número de rotações (0-4)
    """
    return ((key2 % 100) * (pos + 1)) % 5


def rotacionar_direita(texto: str, n: int) -> str:
    """
    Rotaciona string para a direita em n posições
    
    Exemplo: rotacionar_direita("abcde", 2) -> "deabc"
    """
    if n == 0 or n >= len(texto):
        return texto
    return texto[-n:] + texto[:-n]


def rotacionar_esquerda(texto: str, n: int) -> str:
    """
    Rotaciona string para a esquerda em n posições
    
    Exemplo: rotacionar_esquerda("abcde", 2) -> "cdeab"
    """
    if n == 0 or n >= len(texto):
        return texto
    return texto[n:] + texto[:n]


def encrypt(texto: str, key1: int, key2: int) -> str:
    """
    Criptografa um texto usando o sistema homofônico
    
    Args:
        texto: Texto plano a ser criptografado
        key1: Chave primária (0-999)
        key2: Chave secundária (0-999)
    
    Returns:
        String criptografada com prefixo "S:"
    """
    # Validação das chaves
    if not (0 <= key1 <= 999) or not (0 <= key2 <= 999):
        raise ValueError("Keys must be between 0 and 999")
    
    # Gera o mapa de substituição
    mapa = gerar_mapa(key1)
    
    resultado = []
    
    for pos, char in enumerate(texto):
        # Normaliza o caractere
        char_norm = normalizar_caractere(char)
        
        # Obtém a representação do caractere
        if char_norm not in mapa:
            # Se ainda não encontrou, tenta mais uma normalização
            if char_norm in NORMALIZACAO:
                char_norm = NORMALIZACAO[char_norm]
            if char_norm not in mapa:
                resultado.append("?????")
                continue
        
        representacao = mapa[char_norm]
        
        # Aplica rotação baseada na posição
        rot = calcular_rotacao(key2, pos)
        rotacionado = rotacionar_direita(representacao, rot)
        
        resultado.append(rotacionado)
    
    return "S:" + ''.join(resultado)


def decrypt(cifra: str, key1: int, key2: int) -> str:
    """
    Descriptografa uma cifra produzida pelo sistema homofônico
    
    Args:
        cifra: String criptografada (deve começar com "S:")
        key1: Chave primária (0-999)
        key2: Chave secundária (0-999)
    
    Returns:
        Texto plano decifrado
    """
    # Validação das chaves
    if not (0 <= key1 <= 999) or not (0 <= key2 <= 999):
        raise ValueError("Keys must be between 0 and 999")
    
    # Remove o prefixo "S:"
    if not cifra.startswith("S:"):
        raise ValueError("Invalid ciphertext: must start with 'S:'")
    
    cifrado = cifra[2:]
    
    # Gera o mapa reverso
    mapa = gerar_mapa(key1)
    mapa_reverso = {v: k for k, v in mapa.items()}
    
    resultado = []
    pos = 0
    
    # Processa em blocos de 5 caracteres
    for i in range(0, len(cifrado), 5):
        bloco = cifrado[i:i+5]
        
        # Se bloco incompleto, adiciona "?" e continua
        if len(bloco) < 5:
            resultado.append("?")
            continue
        
        # Aplica rotação inversa
        rot = calcular_rotacao(key2, pos)
        original = rotacionar_esquerda(bloco, rot)
        
        # Busca o caractere correspondente
        if original in mapa_reverso:
            resultado.append(mapa_reverso[original])
        else:
            resultado.append("?")
        
        pos += 1
    
    return ''.join(resultado)


def verificar_colisoes(key1: int) -> Tuple[int, int]:
    """
    Verifica se há colisões no mapa gerado pela chave
    
    Args:
        key1: Chave a ser testada
    
    Returns:
        Tupla (total_caracteres, num_colisoes)
    """
    mapa = gerar_mapa(key1)
    reprs = {}
    colisoes = 0
    
    for char, repr_str in mapa.items():
        if repr_str in reprs:
            print(f"COLISÃO: '{char}' e '{reprs[repr_str]}' = '{repr_str}'")
            colisoes += 1
        reprs[repr_str] = char
    
    total = len(mapa)
    print(f"Total: {total} caracteres, {colisoes} colisões")
    return total, colisoes


def mostrar_caracteres_suportados() -> None:
    """Exibe lista de caracteres suportados pelo sistema"""
    print("═" * 50)
    print("CARACTERES SUPORTADOS (69 total):")
    print("═" * 50)
    print()
    print("Letras minúsculas:")
    print("  a b c d e f g h i j k l m n o p q r s t u v w x y z")
    print()
    print("Letras MAIÚSCULAS:")
    print("  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z")
    print()
    print("Números:")
    print("  0 1 2 3 4 5 6 7 8 9")
    print()
    print("Caracteres especiais:")
    print('  [espaço] . ( ) " ! ?')
    print()
    print("═" * 50)
    print("NORMALIZAÇÕES AUTOMÁTICAS:")
    print("═" * 50)
    print()
    print("Acentos removidos:")
    print("  á à â ã ä → a")
    print("  é è ê ë → e")
    print("  í ì î ï → i")
    print("  ó ò ô õ ö → o")
    print("  ú ù û ü → u")
    print("  ç → c")
    print()
    print("Pontuação convertida:")
    print("  , ; : → .")
    print("  - _ → [espaço]")
    print()
    print("Outros caracteres → [espaço]")
    print("═" * 50)


def testar_completo() -> bool:
    """Executa bateria completa de testes automáticos"""
    print("🧪 EXECUTANDO TESTES AUTOMÁTICOS")
    print("=" * 50)
    
    # Testes de colisão
    print()
    print("Verificando colisões nas chaves de teste...")
    for k1 in [123, 111, 789, 333, 555, 777, 999, 100, 50, 1]:
        print(f"  k1={k1}: ", end="")
        _, colisoes = verificar_colisoes(k1)
    
    print()
    print("Testando criptografia/descriptografia...")
    
    testes = [
        ("oi", 123, 456),
        ("abc", 111, 222),
        ("teste", 789, 123),
        ("123", 333, 444),
        ("A B", 555, 666),
        ("hello", 777, 888),
        ("WORLD", 999, 111),
        ("Ola mundo", 100, 200),
        ("Test 123.", 50, 75),
        ("a", 1, 1),
        ("xyz", 999, 0),
        ("Ola!", 200, 300),
        ("(teste)", 400, 500),
        ("Sim ou nao?", 600, 700),
        ("E ai?", 700, 100),
        ("Oi (tudo bem)!", 250, 350),
        ("áéíóú", 123, 456),  # Teste com acentos
        ("çãõ", 456, 789),     # Teste com cedilha e til
    ]
    
    passaram = 0
    total = len(testes)
    
    for texto, k1, k2 in testes:
        print()
        print(f"▶ Teste: '{texto}' (k1={k1}, k2={k2})")
        
        cifra = encrypt(texto, k1, k2)
        print(f"  Cifra: {cifra[:50]}...")
        
        decifrado = decrypt(cifra, k1, k2)
        print(f"  Decif: '{decifrado}'")
        
        # Normaliza o texto original para comparação
        texto_norm = ''.join(normalizar_caractere(c) for c in texto)
        
        if texto_norm == decifrado:
            print("  ✅ PASSOU")
            passaram += 1
        else:
            print(f"  ❌ FALHOU (esperado: '{texto_norm}', obtido: '{decifrado}')")
    
    print()
    print("=" * 50)
    print(f"Resultado: {passaram}/{total} testes passaram")
    print()
    
    return passaram == total


# ========== CLI INTERACTIVA ==========
def main():
    """Interface de linha de comando interativa"""
    import os
    import sys
    
    # Limpa a tela
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("╔" + "═" * 48 + "╗")
    print("║  SISTEMA DE CRIPTOGRAFIA HOMOFÔNICA           ║")
    print("║          Versão Python - Compatível           ║")
    print("║   Suporte a: ( ) \" ! ? e área de transferência║")
    print("╚" + "═" * 48 + "╝")
    print()
    
    if testar_completo():
        print("🎉 TODOS OS TESTES PASSARAM! Sistema validado.")
    else:
        print("⚠️  Alguns testes falharam")
        resposta = input("Continuar mesmo assim? (s/n): ")
        if resposta.lower() != 's':
            sys.exit(1)
    
    input("\nPressione ENTER para continuar...")
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("╔" + "═" * 48 + "╗")
        print("║              MENU PRINCIPAL                   ║")
        print("╚" + "═" * 48 + "╝")
        print()
        print("  [c] Criptografar mensagem")
        print("  [d] Descriptografar mensagem")
        print("  [v] Verificar colisões em uma chave")
        print("  [s] Ver caracteres suportados")
        print("  [t] Executar testes novamente")
        print("  [q] Sair")
        print()
        
        escolha = input("Escolha: ").lower()
        
        if escolha == 'c':
            os.system('clear' if os.name == 'posix' else 'cls')
            print("═══ CRIPTOGRAFAR ═══")
            print()
            
            texto = input("Texto: ").strip()
            if not texto:
                print("❌ Texto vazio!")
                input("Pressione ENTER...")
                continue
            
            try:
                k1 = int(input("Key1 (0-999): "))
                k2 = int(input("Key2 (0-999): "))
                
                if not (0 <= k1 <= 999) or not (0 <= k2 <= 999):
                    raise ValueError
                
                print()
                print("⏳ Gerando mapa sem colisões...")
                cifra = encrypt(texto, k1, k2)
                
                print()
                print("━" * 50)
                print("🔐 CIFRADO:")
                print(cifra)
                print("━" * 50)
                print()
                
            except ValueError:
                print("❌ Chaves inválidas! Use números entre 0 e 999.")
                input("Pressione ENTER...")
                continue
            
            input("Pressione ENTER...")
        
        elif escolha == 'd':
            os.system('clear' if os.name == 'posix' else 'cls')
            print("═══ DESCRIPTOGRAFAR ═══")
            print()
            
            cifra = input("Cifra: ").strip()
            if not cifra or not cifra.startswith("S:"):
                print("❌ Cifra inválida! Deve começar com 'S:'")
                input("Pressione ENTER...")
                continue
            
            try:
                k1 = int(input("Key1: "))
                k2 = int(input("Key2: "))
                
                if not (0 <= k1 <= 999) or not (0 <= k2 <= 999):
                    raise ValueError
                
                print()
                print("⏳ Descriptografando...")
                texto = decrypt(cifra, k1, k2)
                
                print()
                print("━" * 50)
                print("📝 TEXTO DESCRIPTOGRAFADO:")
                print(texto)
                print("━" * 50)
                print()
                
            except ValueError:
                print("❌ Chaves inválidas! Use números entre 0 e 999.")
                input("Pressione ENTER...")
                continue
            
            input("Pressione ENTER...")
        
        elif escolha == 'v':
            os.system('clear' if os.name == 'posix' else 'cls')
            print("═══ VERIFICAR COLISÕES ═══")
            print()
            
            try:
                k1 = int(input("Key1 para verificar: "))
                print()
                print("⏳ Verificando...")
                _, colisoes = verificar_colisoes(k1)
                print()
                
                if colisoes == 0:
                    print("✅ Esta chave está segura (sem colisões)!")
                else:
                    print("⚠️  Esta chave tem colisões! Escolha outra.")
                
            except ValueError:
                print("❌ Chave inválida!")
            
            print()
            input("Pressione ENTER...")
        
        elif escolha == 's':
            os.system('clear' if os.name == 'posix' else 'cls')
            mostrar_caracteres_suportados()
            print()
            input("Pressione ENTER...")
        
        elif escolha == 't':
            os.system('clear' if os.name == 'posix' else 'cls')
            testar_completo()
            print()
            input("Pressione ENTER...")
        
        elif escolha == 'q':
            os.system('clear' if os.name == 'posix' else 'cls')
            print("👋 Até logo!")
            print()
            print("Lembre-se: Suas chaves são secretas!")
            print("Sem elas, não há como recuperar os dados.")
            print()
            sys.exit(0)
        
        else:
            print("❌ Opção inválida!")
            input("Pressione ENTER...")


if __name__ == "__main__":
    main()
