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
#	Descricao: Daemon exemplo para conexao com a catraca da Henry7X,
#	necessita da biblioteca henry7x.
#
#=======================================================================

import socket
import datetime
import time
import henry7x as catraca
import re
import logging
import logging.handlers
import argparse
import sys
import errno


# Valores padrao
HOST = '192.168.1.5'							# Endereco IP da Catraca, definido utilizando o programa da Henry 7X
PORT = 3000										# Porta da Catraca, definida utilizando o programa da Henry 7X
tempoTimeout = 60								# Timeout da conexao 
tempoCatracaLiberada = 10						# Tempo que a catraca permanece destravada
LOG_FILENAME = "catracaDaemon.log"		# Arquivo de Log da catraca
LOG_LEVEL = logging.INFO 						# Nivel de Log
debugDados = False								# Auxiliar para debuggar dados recebidos

# Definindo configuracoes personalizadas
parser = argparse.ArgumentParser(description="Controle de Acesso NUPEDEE - Catraca Henry7x")
parser.add_argument("-l", "--log", help="Arquivo para o log (padrao: '" + LOG_FILENAME + "')")
parser.add_argument("-x", "--host", help="Host da catraca (padrao: '" + HOST + "')")
parser.add_argument("-p", "--porta", help="Porta do Host da catraca (padrao: '" + repr(PORT) + "')")
parser.add_argument("-t", "--timeout", help="Tempo do Timeout da conexao (padrao: '" + repr(tempoTimeout) + "')")
parser.add_argument("-c", "--tcatraca", help="Tempo da catraca liberada (padrao: '" + repr(tempoCatracaLiberada) + "')")


# Verifica se passou argumentos e atualiza as globais
args = parser.parse_args()
if args.log:
	LOG_FILENAME = args.log
if args.host:
	HOST = args.host
if args.porta:
	PORT = int(args.porta)
if args.timeout:
	tempoTimeout = int(args.timeout)

# Configuracoes do logger, rotatividade, etc.
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=0)
formatter = logging.Formatter('[%(asctime)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Classe do Logger
class LoggerCatraca(object):
	def __init__(self, logger, level):
		# Argumentos Default
		self.logger = logger
		self.level = level
	def write(self, message):
		#LOG_UNIQUE_ID = 1002 + 1
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			#message = "["+repr(LOG_UNIQUE_ID).zfill(12)+"] "+message
			self.logger.log(self.level, message.rstrip())


# Trasnforma a saida padrao/erros do programa em log
sys.stdout = LoggerCatraca(logger, logging.INFO)
sys.stderr = LoggerCatraca(logger, logging.ERROR)

print("\n\n# Iniciando log de "+time.strftime("%c")+"\n");
print("==== Inicializando")

while(True):
	try:
		# Inicializa conexao por socket
		print("[Socket] Tentando se conectar com '"+str(HOST)+":"+str(PORT)+"' (Catraca)")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		s.settimeout(tempoTimeout)
		print("[Socket] Timeout setado para "+repr(tempoTimeout)+" segundos.")

		print("[Socket] Conectado!")

		while(True):
			print("\n\n###################################################################################")
			print("[Comunicacao] Aguardando receber 8 bytes (Header)...")
			#header = s.recv(8)

			# Codigo abaixo para receber 1 byte por vez ao inves de pedir todos para o socket
			# Por algum motivo receber todos juntos nao funciona (ele recebe menos que o requisitado algumas vezes)
			header = bytearray()
			qtdBytesLidos = 1
			while(len(header) < 8):
				leitura = s.recv(1)
				#print("\tRecebido bytes "+repr(qtdBytesLidos)+"/8")
				if(len(leitura) == 1):
					header.append(leitura[0])
					qtdBytesLidos += 1
							

			# Debug Header
			if debugDados:
				print("Todos os bytes recebidos ok.")
				stringHex = ""
				for x in header:
					stringHex = stringHex + "0x"+format(x,'02x')+" "
				print("[Header] "+stringHex+"\n")

			# Calcula Checksum Xor do Header
			checksumHeader = catraca.gerarChecksum(header[0:6])
			checksumHeaderRecebido = header[7]
			if(checksumHeader != checksumHeaderRecebido):	# Se for diferente do que veio, tem problema
				print("Mensagem invalida recebida: Checksum do HEADER nao confere!")
				print("\tRecebido/Calculado: "+format(checksumHeaderRecebido,'02x')+"/"+format(checksumDados,'02x'))
				continue
			else:
				print("[Comunicacao] Header OK! (Calculado: "+format(checksumHeader,'02x')+", Recebido: "+format(checksumHeaderRecebido,'02x')+")")


			# Testa se foi recebido um ACK ou dados
			# 0x01 0x80 -> ACK
			if(header[0] == 1 and header[1] == 128):
				print("[Comunicacao] Recebido ACK (sem dados)")
				ACK = header[3]
				if(ACK == 0):
					print("[Comunicacao] ACK Ok")
				elif(ACK == 1):
					print("[Comunicacao - Erro] Comando inv./relido foi recebido")
				elif(ACK == 2):
					print("[Comunicacao - Erro] Versao Imcompativel")
				elif(ACK == 3):
					print("[Comunicacao - Erro] Status Errado foi recebido")
				elif(ACK == 4):
					print("[Comunicacao - Erro] Tamanho dos Registradores diferentes foi recebido")
				elif(ACK == 5):
					print("[Comunicacao - Erro] Numero dos Registradores invalido foi recebido")
				elif(ACK == 6):
					print("[Comunicacao - Erro] Cabecalho com erro de checksum")
				else:
					print("[Comunicacao - Erro] Algum outro erro ocorreu: "+repr(ACK))
				continue
			elif(header[0] == 1 and header[1] == 144):		# 0x01 0x90 -> Bilhete
				# Dados recebidos, nada a fazer de especial, apenas continuar o codigo e fazer o processamento dos dados recebidos
				pass
			else:
				# Alguma coisa de muito estranho aconteceu. Isso nao deve acontecer nunca, mas esta ai so por claridade
				print("[Comunicacao - Erro] Header Desconhecido recebido!")
				respostaErro = catraca.geraMensagem("Tente Novamente!","Header Desc.",10,catraca.ACESSO_NEGADO)
				s.sendall(respostaErro)
				print("[Comunicacao] Resposta enviada")
				continue

			# Se chegou ate aqui esta tudo bem com o header e e um bilhete com dados!
			# Pega o tamanho dos dados do header e requisita os mesmos do socket
			qtdDados = int(header[catraca.TamanhoMsg])
			dados = bytearray()
			print("[Comunicacao] Recebido Header para comunicacao de dados ("+repr(qtdDados)+" bytes)")
			print("[Comunicacao] Aguardando receber "+repr(qtdDados)+" bytes (Dados)...")


			# Codigo abaixo para receber 1 byte por vez ao inves de pedir todos para o socket (usando dados = s.recv(qtdDados), por exemplo)
			# Por algum motivo receber todos juntos nao funciona (ele recebe menos que o requisitado algumas vezes)
			dados = bytearray()
			qtdBytesLidos = 1
			while(len(dados) < qtdDados):
				leitura = s.recv(1)
				#print("\tRecebido bytes "+repr(qtdBytesLidos)+"/"+repr(qtdDados))
				if(len(leitura) == 1):
					dados.append(leitura[0])
					qtdBytesLidos += 1

			chkDados = s.recv(1)			# O ultimo byte a receber e o checksum
			chkDados = int(chkDados[0])

			# Debug dados
			if debugDados:
				print("Todos os bytes recebidos ok.")
				stringHex = ""
				for x in dados:
					stringHex = stringHex + "0x"+format(x,'02x')+" "

				stringHex = stringHex + "0x"+format(chkDados,'02x')
				print("[Dados] "+stringHex+"\n")

			# Calcula Checksum Xor dos dados
			checksumDados = catraca.gerarChecksum(dados[0:qtdDados])

			if(chkDados != checksumDados):
				print("Mensagem invalida recebida: Checksum dos DADOS nao confere!")
				print("\tRecebido/Calculado: "+format(chkDados,'02x')+"/"+format(checksumDados,'02x'))
				continue
			else:
				print("[Checksum] Dados OK! (Calculado: "+format(checksumDados,'02x')+", Recebido: "+format(chkDados,'02x')+")")

			# Comeco do algoritmo
			Matricula = catraca.getMatricula(dados,qtdDados)
					
			data_hora = catraca.getHora(dados)
			data_minutos = catraca.getMinutos(dados)
			data_segundos = catraca.getSegundos(dados)
			data_dia = catraca.getDia(dados)
			data_mes = catraca.getMes(dados)
			data_ano = catraca.getAno(dados)

			# Verifica o valor do ano, que pode representar um movimento da catraca
			TextoOpCatraca = "Catraca foi Girada"
			OpCatraca = 0
			responder = True
			agora = datetime.datetime.now()
			if(data_ano == catraca.NaoGirou):
				TextoOpCatraca = "Catraca nao foi girada"
				OpCatraca = catraca.NaoGirou
				data_ano = agora.year
			elif(data_ano == catraca.PortaAberta):
				TextoOpCatraca = "Porta Aberta"
				OpCatraca = catraca.PortaAberta
				data_ano = agora.year
			elif(data_ano == catraca.PortaForcada):
				TextoOpCatraca = "Porta Forcada"
				OpCatraca = catraca.PortaForcada
				data_ano = agora.year
			elif(data_ano == catraca.Botao):
				TextoOpCatraca = "Botao pressionado"
				OpCatraca = catraca.Botao
				data_ano = agora.year
			elif(data_ano == catraca.ErroTempo):
				TextoOpCatraca = "Erro de Tempo"
				OpCatraca = catraca.ErroTempo
				data_ano = agora.year
				responder = False
			else:
				data_ano += 2000
				responder = True


			# Gera um timestamp com a data final, para analisar mais facil futuramente. Ou nunca. Melhor ja ter o codigo pronto
			timestamp = datetime.datetime(data_ano, data_mes, data_dia, data_hora, data_minutos, data_segundos).strftime("%s")

			# Parsing dos dados da Requisicao
			AcessoNegado = catraca.getAcessoNegado(dados)
			TipoMovimento = catraca.getTipoMovimento(dados)
			TipoEntrada = catraca.getTipoEntrada(dados)
			IdFuncao = catraca.getIdFuncao(dados)

			# Apenas para debug
			TextoTipoEntrada = ""
			TextoAcessoNegado = ""

			if TipoEntrada == catraca.Teclado:
				TextoTipoEntrada = "Teclado"
			elif TipoEntrada == catraca.Cracha:
				TextoTipoEntrada = "Cracha"
			elif TipoEntrada == catraca.Digital1n:
				TextoTipoEntrada = "Digital1n"
			elif TipoEntrada == catraca.Digital11:
				TextoTipoEntrada = "Digital11"

			if AcessoNegado == 0:
				TextoAcessoNegado = "Nao"
			else:
				TextoAcessoNegado = "Sim"

			MovPalavra = "Entrada de Dados"
			# Debug dos Dados interpretados, para analise
			print("---------------------------------------------")
			print("[Informacoes extraidas do bilhete]")
			print('\tData/Hora: '+repr(data_hora)+':'+repr(data_minutos)+':'+repr(data_segundos)+' '+repr(data_dia)+'/'+repr(data_mes)+'/'+repr(data_ano))
			print("\tMatricula: "+Matricula)
			print("\tTipoDados: "+TextoTipoEntrada)
			print("\tAcessoNeg: "+TextoAcessoNegado)
			print("\tOperacao : "+TextoOpCatraca)
			print("\tId Funcao: "+repr(IdFuncao))
			print("---------------------------------------------")


			# Neste ponto do codigo e preciso fazer o processamento dos dados recebidos e decidir o que deve acontecer com a catraca

			# Exemplos dos tipos de resposta possiveis com o sistema
			if (int(Matricula) == "10000"):
				# Negar
				# A catraca emite alguns bips e nao libera. A mensagem tambem e exibida na tela
				resposta = catraca.geraMensagem("Voce foi negado!","Que pena, amigo!",tempoCatracaLiberada,catraca.ACESSO_NEGADO)
			elif (int(Matricula) == "10001"):
				# Liberar apenas entrada
				# A catraca permite um movimento anti-horario apenasm, bloqueando pelo outro lado. Bip emitido
				resposta = catraca.geraMensagem("Permitei girar","mas so pra la <<",tempoCatracaLiberada,catraca.LIBERAR_ENTRADA)
			elif (int(Matricula) == "10002"):
				# Liberar apenas saida
				# A catraca permite um movimento horario apenasm, bloqueando pelo outro lado. Bip emitido
				resposta = catraca.geraMensagem("Permitei girar","mas so pra la >>",tempoCatracaLiberada,catraca.LIBERAR_SAIDA)
			elif (int(Matricula) == "10003"):
				# Liberar Ambos
				# Catraca fica liberada para qualquer lado. Bip emitido
				resposta = catraca.geraMensagem("Permitirei girar","pra qqr lado!",tempoCatracaLiberada,catraca.LIBERAR_AMBOS)
			else:
				# Apenas mensagem
				# Nada acontece com a catra, apenas uma mensagem e exibida na tela. Sem som
				resposta = catraca.geraMensagem("Frase com 32 car","acteres aqui....",tempoCatracaLiberada,catraca.SOMENTE_MSG)
			
			# Envia resposta gerada
			s.sendall(resposta)
	except socket.error as se:
		if se.errno == None:
			if s:
				s.close()
			print("[Socket] Timeout de dados estourado, reconectando conexao.")
		else:
			print("[Socket] Erro de Conexao ("+repr(se.errno)+"), reconectando...")
	except socket.timeout:
		print("[Socket] Nao recebi dados por "+repr(tempoTimeout)+", reiniciando conexao...")
	except KeyboardInterrupt:
		print("[Final] Recebido comando de saida, finalizando.")
		if s:
			s.close()
		raise
	except SystemExit:
		print("[Final] Recebido comando de saida, finalizando.")
		if s:
			s.close()
		raise
