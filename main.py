# Importar elementos necessários para o app

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import requests
import re
from kivy.uix.screenmanager import ScreenManager, Screen

# Carregamento da tela

Builder.load_file('tela.kv')

# Declaração das screens

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = None

    def realizar_login(self):
        """Faz login no Supabase e obtém o token de autenticação."""
        email = self.ids.usuario.text
        senha = self.ids.senha.text

        if not email or not senha:
            self.ids.mensagem_erro.text = "Por favor, preencha todos os campos."
            return

        url = "https://yyppatzbgrdettscyunq.supabase.co/auth/v1/token?grant_type=password"
        headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cHBhdHpiZ3JkZXR0c2N5dW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MjExMjAsImV4cCI6MjA0ODQ5NzEyMH0.bOZ3smY_-GUY2wTckc0cdn5eXetVASkTUt6eK_WZ6xE", 
            "Content-Type": "application/json"
        }
        
        dados = {
            "email": email,
            "password": senha,
        }

        try:
            resposta = requests.post(url, json=dados, headers=headers)

            if resposta.status_code == 200:
                # Extrai o token da resposta
                self.token = resposta.json().get("access_token")
                
                if self.token:
                    self.salvar_token(self.token)  # Salva o token para uso posterior
                    self.manager.current = "escolherdog"  # Direciona para a EscolherDogScreen
                else:
                    self.ids.mensagem_erro.text = "Erro ao obter o token. Tente novamente."
            else:
                self.ids.mensagem_erro.text = "Login inválido. Verifique os dados."
        except requests.exceptions.RequestException as e:
            print(f"Erro ao realizar login: {e}")
            self.ids.mensagem_erro.text = "Erro ao conectar ao servidor. Tente novamente."
    # Armazena o token de acesso
    def salvar_token(self, token):
        """Salva o token para uso em futuras requisições."""
        token = self.token  
        print(f"\nToken de autenticação: {token}\n")
        return token


class EscolherDogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token = None
        self.dogs = []
        self.dog_selecionado = None  # Variável para armazenar o cachorro selecionado

    def on_enter(self):
        """Quando a tela for acessada, tenta recuperar o token e buscar os cachorros do usuário."""
        login_screen = self.manager.get_screen('login')  # Obtém a instância de LoginScreen
        if hasattr(login_screen, 'token') and login_screen.token:
            self.token = login_screen.token
            print(f"\nToken de autenticação reload: {self.token}\n")
            self.carregar_cachorros()  # Carrega os cachorros registrados
        else:
            print("Token não encontrado ou inválido. Redirecionando para Login.")
            self.manager.current = 'login'  # Redireciona para a tela de login caso o token não seja encontrado

    def carregar_cachorros(self):
        """Faz uma requisição para buscar os cachorros registrados do usuário no Supabase."""
        url = "https://yyppatzbgrdettscyunq.supabase.co/rest/v1/dogs?"
        headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cHBhdHpiZ3JkZXR0c2N5dW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MjExMjAsImV4cCI6MjA0ODQ5NzEyMH0.bOZ3smY_-GUY2wTckc0cdn5eXetVASkTUt6eK_WZ6xE",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        try:
            resposta = requests.get(url, headers=headers)
            if resposta.status_code == 200:
                self.dogs = resposta.json()
                self.exibir_cachorros()
            elif resposta.status_code == 401:
                print("Token expirado. Redirecionando para Login")
                self.manager.current = 'login'
            else:
                print("Erro ao acessar os cachorros.")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar os cachorros: {e}")

    def exibir_cachorros(self):
        """Exibe os cachorros em um spinner para o usuário selecionar."""
        spinner = self.ids.spinner_dogs
        spinner.values = [dog['nome'] for dog in self.dogs]  # Assume que 'nome' é o campo que queremos exibir
        spinner.bind(on_text=self.on_dog_select)
        self.ids.btn_acessar.disabled = True  # Desabilita o botão inicialmente

    def on_dog_select(self, spinner, text):
        """Quando o usuário selecionar um cachorro, salva o ID e direciona para MeuDogScreen."""
        self.dog_selecionado = next((dog for dog in self.dogs if dog['nome'] == text), None)
        if self.dog_selecionado:
            self.ids.btn_acessar.disabled = False  # Habilita o botão após a seleção
    def acessar_dog(self):
        """Ao clicar no botão Acessar, direciona o usuário para a tela MeuDog."""
        if self.dog_selecionado:
            # Passa o ID do cachorro selecionado para a tela MeuDog
            self.manager.get_screen('meudog').set_dog(self.dog_selecionado['id'])
            self.manager.current = 'meudog'  # Direciona para MeuDogScreen

class MeuDogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dog_id = None

    def set_dog(self, dog_id):
        """Define o cachorro selecionado para ser exibido na tela MeuDog."""
        self.dog_id = dog_id
        print(f"ID do cachorro selecionado: {self.dog_id}")
        self.carregar_dados_do_cachorro()

    def carregar_dados_do_cachorro(self):
        """Carrega os dados do cachorro selecionado utilizando o ID."""
        if self.dog_id:
            url = f"https://yyppatzbgrdettscyunq.supabase.co/rest/v1/dogs?id=eq.{self.dog_id}"
            headers = {
                "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cHBhdHpiZ3JkZXR0c2N5dW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MjExMjAsImV4cCI6MjA0ODQ5NzEyMH0.bOZ3smY_-GUY2wTckc0cdn5eXetVASkTUt6eK_WZ6xE",
                "Authorization": f"Bearer {self.manager.get_screen('login').token}",
                "Content-Type": "application/json"
            }

            try:
                resposta = requests.get(url, headers=headers)
                if resposta.status_code == 200:
                    dados_dog = resposta.json()
                    print(f"Dados do cachorro: {dados_dog}")
                    # Exibir os dados na interface, como nome, histórico, etc.
                
                else:
                    print("Erro ao carregar dados do cachorro.")
            except requests.exceptions.RequestException as e:
                print(f"Erro ao acessar os dados do cachorro: {e}")



class CadastroScreen(Screen):
    def on_enter(self):
        """Carregar dados de estados ao entrar na tela"""
        self.ids.estado.values = self.get_states()
        self.ids.cidade.values = []

    def get_states(self):
        """Buscar Estados através de uma API pública"""
        url = "https://brasilapi.com.br/api/ibge/uf/v1"
        try:
            resposta = requests.get(url)
            estados = [estado['sigla'] for estado in resposta.json()]
            # estado_selecionado = self.ids.estado.text
            return estados
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar estados: {e}")
            return []
    
    def get_cities(self, text):
        """Buscar cidades de um estado específico"""
        url = f"https://brasilapi.com.br/api/ibge/municipios/v1/{text}"
        try:
            resposta = requests.get(url)
            cidades = [cidade['nome'] for cidade in resposta.json()]
            return cidades
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar cidades para o estado {text}: {e}")
            return []
    
    def on_estado_select(self, spinner, text):
        """Carregar cidades quando um estado for selecionado"""
        if text != "Selecione o Estado":  # Certifica-se de que um estado válido foi selecionado
            cidades = self.get_cities(text)  # Passa apenas o texto do estado para a função
            self.ids.cidade.values = cidades  # Atualiza o spinner de cidades com os resultados
            self.ids.cidade.text = "Selecione a cidade"  # Define o texto inicial para o spinner de cidades

    def enviar_cadastro(self):
        """Enviar os dados do cadastro para o Supabase."""
        nome = self.ids.usuario.text
        senha = self.ids.senha.text
        email = self.ids.email.text
        estado = self.ids.estado.text
        cidade = self.ids.cidade.text

        # Validar os dados
        mensagem_erro = self.validar_entrada(nome, senha, email, estado, cidade)
        if mensagem_erro:
            self.ids.mensagem_erro.text = mensagem_erro
            return

        # Criar usuário no Supabase Auth e capturar o token
        token = self.criar_usuario_supabase(email, senha)
        if token:
            # Enviar dados adicionais para a tabela de usuários no Supabase
            url = "https://yyppatzbgrdettscyunq.supabase.co/rest/v1/usuarios?"
            headers = {
                "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cHBhdHpiZ3JkZXR0c2N5dW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MjExMjAsImV4cCI6MjA0ODQ5NzEyMH0.bOZ3smY_-GUY2wTckc0cdn5eXetVASkTUt6eK_WZ6xE",
                "Authorization": f"Bearer {token}",  # Autenticação usando o token JWT
                "Content-Type": "application/json",
            }
            dados = {
                "nome": nome,
                "email": email,
                "estado": estado,
                "cidade": cidade,
            }
            print(f"Enviando requisição para {url} com headers {headers} e dados {dados}")
            try:
                resposta = requests.post(url, json=dados, headers=headers)

                # Log detalhado em caso de erro
                if resposta.status_code != 201:
                    print(f"Erro ao criar usuário na tabela: {resposta.status_code} - {resposta.text}")
                
                # Verificar a resposta
                if resposta.status_code == 201:
                    self.ids.mensagem_erro.text = "Cadastro realizado com sucesso!"
                    self.ids.mensagem_erro.color = (47, 79, 47, 1)  # Verde escuro
                elif resposta.status_code == 409:
                    self.ids.mensagem_erro.text = "E-mail já cadastrado."
                else:
                    self.ids.mensagem_erro.text = "Erro no cadastro. Tente novamente."
            except requests.exceptions.RequestException as e:
                print(f"Erro ao enviar dados adicionais: {e}")
                self.ids.mensagem_erro.text = "Erro no envio dos dados. Tente novamente."
        else:
            self.ids.mensagem_erro.text = "Erro ao criar usuário no Supabase Auth."



    def criar_usuario_supabase(self, email, senha):
        """Criar usuário no Supabase Auth."""
        url = "https://yyppatzbgrdettscyunq.supabase.co/auth/v1/signup"
        headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cHBhdHpiZ3JkZXR0c2N5dW5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MjExMjAsImV4cCI6MjA0ODQ5NzEyMH0.bOZ3smY_-GUY2wTckc0cdn5eXetVASkTUt6eK_WZ6xE",
            "Content-Type": "application/json",
        }
        dados = {
            "email": email,
            "password": senha,
        }
        try:
            resposta = requests.post(url, json=dados, headers=headers)
            if resposta.status_code == 200 or resposta.status_code == 201:
                # Captura o token JWT do Supabase
                token = resposta.json().get("access_token")
                return token
            else:
                print(f"Erro ao criar usuário: {resposta.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao criar usuário no Supabase Auth: {e}")
            return None


    def validar_entrada(self, nome, senha, email, estado, cidade):
        """Validar os campos do formulário."""
        # Nome: obrigatório e com no máximo 50 caracteres
        if not nome or len(nome) > 50:
            return "Nome inválido! Máx: 50 caracteres."

        # Senha: obrigatória, com letras, números e caracteres especiais
        if (
            not senha
            or len(senha) > 20
            or not re.search(r"[A-Za-z]", senha)
            or not re.search(r"[0-9]", senha)
            or not re.search(r"[!@#$%^&*()_+=\-{};:'\"|,.<>?/]", senha)
        ):
            return "Senha inválida! Máx: 20 caracteres, com letras, números e símbolos."

        # E-mail: formato válido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "E-mail inválido!"

        # Cidade e Estado: obrigatórios
        if not estado or not cidade or estado == "Selecione o Estado" or cidade == "Selecione a cidade":
            return "Cidade e Estado são obrigatórios."

        return None

# Buid do app

class DogApp(App):

    def build(self):
        sm = ScreenManager()
        self.title = "I Love My Dog"
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CadastroScreen(name='cadastro'))
        sm.add_widget(EscolherDogScreen(name='escolherdog'))
        sm.add_widget(MeuDogScreen(name='meudog'))

        return sm

if __name__ == '__main__':
    DogApp().run()