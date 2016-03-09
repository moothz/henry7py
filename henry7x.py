#=======================================================================
#	                        _   _         
#	                       | | | |        
#	  _ __ ___   ___   ___ | |_| |__  ____
#	 | '_ ` _ \ / _ \ / _ \| __| '_ \|_  /
#	 | | | | | | (_) | (_) | |_| | | |/ / 
#	 |_| |_| |_|\___/ \___/ \__|_| |_/___|
#
#	Autor: Jeann Carlo Martins Raguzzoni (moothz)
#	Email: moothz@ufsm.br
#	Descricao: Biblioteca para integracao da catraca da Henry7X
#	utilizando a linguagem python.
#
#=======================================================================

##### Parsers Pacote 'BILHETE'
# Todos estes dados foram retirados de um documento fornecido pela Henry7X
# Posicoes
TamanhoMsg = 5
ChkCom = 7

TipoBilhete = 0
TipoFuncao = 1
Ano = 2
MesSegundos = 3
DiaHora = 4
Minutos = 5

# Mascaras TipoBilhete
FlagEntrada =		int('00000001',2)	# 0 = Entrada, 1 = Saida
FlagMaster = 		int('00000010',2)	# 1 = Liberou
FlagTipo = 			int('00001100',2)	# Tipo de Entrada (0 = Teclado; 1 = Cracha; 2 = Digital 1:n; 3 = Digital 1:1)
FLiberou = 			int('00010000',2)	# Funcao Liberou
AceNeg = 			int('00100000',2)	# Acesso Negado
TipoNeg = 			int('11000000',2)	# Motivo da Negacao (0 = Senha; 1 = Nivel; 2 = Horario 1:n; 3 = Empresa 1:1)
FlagEntrada_Shift = 0
Master_Shift = 1
FlagTipo_Shift = 2
FLiberou_Shift = 4
AceNeg_Shift = 5
TipoNeg_Shift = 6

# Mascaras TipoFuncao
ValorFunc = 		int('01111111',2)	# Valor da funcao (0..100, 0 = Nenhuma)
MascSeg_Bit4 = 		int('10000000',2)	# Bit 4 dos Segundos
ValorFunc_Shift = 0
MascSeg_Bit4_Shift = 3

# Mascaras Ano
MascAno = 			int('01111111',2)	# Valor do Ano (0..99, 0xFF = Nao Girou Catraca, 0xFE = Porta Aberta, 0xFD = Porta Forcada, 0xFC = Botao)
MascSeg_Bit5 = 		int('10000000',2)	# Bit 5 dos Segundos
MascAno_Shift = 0
MascSeg_Bit5_Shift = 2

# Mascaras MesSegundos
MascMes = 			int('00001111',2)	# Valor do Mes (1..12)
MascSeg_Bits03 = 	int('11110000',2)	# Valor dos 4 bits iniciais do Segundo
MascMes_Shift = 0
MascSeg_Bits03_Shift = 4

# Mascaras DiaHora
MascDia_Bits03 = 	int('00001111',2)	# Valor dos 4 bits iniciais do Dia
MascHora_Bits03 = 	int('11110000',2)	# Valor dos 4 bits iniciais da Hora
MascDia_Bits03_Shift = 0
MascHora_Bits03_Shift = 4

# Mascaras Minutos
MascMinutos = 		int('00111111',2)	# Valor dos minutos (0..59)
MascDia_Bit4 = 		int('01000000',2)	# ultimo Bit do Dia
MascHora_Bit4 = 	int('10000000',2)	# ultimo Bit da Hora
MascMinutos_Shift = 0
MascDia_Bit4_Shift = 6
MascHora_Bit4_Shift = 3

##### Parsers Pacote 'ACK'
	
	
# Outros Defines
Teclado = 0
Cracha = 1
Digital1n = 2
Digital11 = 3
Entrada = 0
Saida = 1
Erro_Senha = 0
Erro_Nivel = 1
Erro_Horario = 2
Erro_Empresa = 3

# Respostas da Catraca
NaoGirou = 127
PortaAberta = 126
PortaForcada = 125
Botao = 124
ErroTempo = 121
MovimentoEntrada = 1
MovimentoSaida = 0

# Operacoes da mensagem de resposta
ACESSO_NEGADO = 0
LIBERAR_ENTRADA = 2
LIBERAR_SAIDA = 1
REVISTA = 3
SOMENTE_MSG = 4
LIBERAR_AMBOS = 129

# Operacoes Bitwise pra extrair os dados
# Os dados estao espalhados em varios bytes e ficam 'esconcidos' em uma mascara.
# Deve-se Aplicar a mascara (&) e fazer o shift dos bits (>>) pela quantia necessaria para cada dado
def getHora(dados):
	data_hora = ((int(dados[DiaHora]) & MascHora_Bits03) >> MascHora_Bits03_Shift) | ((int(dados[Minutos]) & MascHora_Bit4) >> MascHora_Bit4_Shift)
	return data_hora
def getMinutos(dados):
	data_minutos = (int(dados[Minutos]) & MascMinutos) >> MascMinutos_Shift
	return data_minutos
def getSegundos(dados):
	data_segundos = ((int(dados[TipoFuncao]) & MascSeg_Bit4) >> MascSeg_Bit4_Shift) | ((int(dados[Ano]) & MascSeg_Bit5) >> MascSeg_Bit5_Shift) | ((int(dados[MesSegundos]) & MascSeg_Bits03) >> MascSeg_Bits03_Shift)
	return data_segundos
def getDia(dados):
	data_dia = ((int(dados[DiaHora]) & MascDia_Bits03) >> MascDia_Bits03_Shift) | ((int(dados[Minutos]) & MascDia_Bit4) >> MascDia_Bit4_Shift)
	return data_dia
def getMes(dados):
	data_mes = (int(dados[MesSegundos]) & MascMes) >> MascMes_Shift
	return data_mes
def getAno(dados):
	data_ano = ((int(dados[Ano]) & MascAno) >> MascAno_Shift)
	return data_ano
def getAcessoNegado(dados):
	AcessoNegado = (int(dados[TipoBilhete]) & AceNeg) >> AceNeg_Shift
	return AcessoNegado
def getTipoMovimento(dados):
	TipoMovimento = (int(dados[TipoBilhete]) & FlagEntrada) >> FlagEntrada_Shift
	return TipoMovimento
def getTipoEntrada(dados):
	TipoEntrada = (int(dados[TipoBilhete]) & FlagTipo) >> FlagTipo_Shift
	return TipoEntrada
def getIdFuncao(dados):
	IdFuncao = (int(dados[TipoFuncao]) & ValorFunc) >> ValorFunc
	return IdFuncao
def getMatricula(dados,fim):
	inicio = 6	# Definido pelo protocolo que comeca o 6
	Matricula = ''
	for x in dados[inicio:fim]:
		Matricula = Matricula+''+format(x,'02x')
	return Matricula


def geraMensagem(linha1,linha2,duracao,operacao):
	# Prepara resposta - "MENSAGEM"
	resposta = bytearray()		# Os valores a seguir definem o header padrao para o tipo "MENSAGEM"
	resposta.append(254)		# 0xFE
	resposta.append(128)		# 0x80
	resposta.append(112)		# 0x70
	resposta.append(0)			# 0x00
	resposta.append(34)			# 0x22
	resposta.append(1)			# 0x01
	resposta.append(0)			# 0x00
	resposta.append(45)			# 0x2D
	resposta.append(operacao)	# 0 = Negado, 1 = Entrada, 2 = Saida, 3 = Revista, 4 = Somente Mensagem, 129 = Ambos os lados

	# A string mensagem deve possuir _exatamente_ 32 caracteres
	if(len(linha1) > 16):
		linha1 = linha1[0:16]
	elif(len(linha1) < 16):
		faltam = 16 - len(linha1)
		for x in range(0, faltam):
			linha1 += " "

	if(len(linha2) > 16):
		linha2 = linha2[0:16]
	elif(len(linha2) < 16):
		faltam = 16 - len(linha2)
		for x in range(0, faltam):
			linha2 += " "
	
	if(duracao < 1):
		duracao = 1
	elif(duracao > 255):
		duracao = 255

	# Converte caracteres em seus valores ASCII e coloca no byte array da resposta
	mensagem = linha1 + linha2
	print("[Catraca] Mensagem Gerada: "+repr(len(mensagem))+" '"+mensagem+"'")
	for c in mensagem:
		resposta.append(ord(c))

	# Aqui e definida a duracao da mensagem, valores de 0 a 255 (0xFF)
	resposta.append(duracao)

	# Calculo do Checksum da Resposta
	checksumResposta = gerarChecksum(resposta)
	# Coloca o checksum no array
	resposta.append(checksumResposta)

	rRaw = ""
	for x in resposta:
		rRaw += format(x,'02x')+" "
	#print("[Catraca] Resposta: "+rRaw)
	return resposta

def geraMensagemErro(linha1,linha2,duracao,operacao):
	# Prepara resposta - "ERRO"
	resposta = bytearray()		# Os valores a seguir definem o header padrao para o tipo "MENSAGEM"
	resposta.append(254)		# 0xFE
	resposta.append(128)		# 0x80
	resposta.append(112)		# 0x70
	resposta.append(0)			# 0x00
	resposta.append(34)			# 0x22
	resposta.append(1)			# 0x01
	resposta.append(0)			# 0x00
	resposta.append(45)			# 0x2D
	resposta.append(0)	# 0 = Negado, 1 = Entrada, 2 = Saida, 3 = Revista, 4 = Somente Mensagem, 129 = Ambos os lados

	# A string mensagem deve possuir _exatamente_ 32 caracteres
	if(len(linha1) > 16):
		linha1 = linha1[0:16]
	elif(len(linha1) < 16):
		faltam = 16 - len(linha1)
		for x in range(0, faltam):
			linha1 += " "

	if(len(linha2) > 16):
		linha2 = linha2[0:16]
	elif(len(linha2) < 16):
		faltam = 16 - len(linha2)
		for x in range(0, faltam):
			linha2 += " "
	
	if(duracao < 1):
		duracao = 1
	elif(duracao > 255):
		duracao = 255

	# Converte caracteres em seus valores ASCII e coloca no byte array da resposta
	mensagem = linha1 + linha2
	print("[Catraca] Mensagem a ser enviada: "+repr(len(mensagem))+" '"+mensagem+"'")
	for c in mensagem:
		resposta.append(ord(c))

	# Aqui e definida a duracao da mensagem, valores de 0 a 255 (0xFF)
	resposta.append(duracao)

	# Calculo do Checksum da Resposta
	checksumResposta = gerarChecksum(resposta)
	# Coloca o checksum no array
	resposta.append(checksumResposta)

	rRaw = ""
	for x in resposta:
		rRaw += format(x,'02x')+" "
	#print("[Catraca] Resposta: "+rRaw)
	return resposta

def gerarChecksum(array):
	checksum = 0
	for x in array:
		checksum ^= x
	return int(checksum)