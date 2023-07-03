from django.test import TestCase
from django.urls import reverse
from Producao.views import CriarColetaView, EditarColetaView, ExibirRelatorioColetaView
import unittest

from Producao import Criacao, Coleta



class TestCriacao(unittest.TestCase):
    def test_tamanho_maximo_id(self):
        criacao = Criacao(id="1234567890", raca="Cachorro", data_entrada="2023-06-01")
        self.assertEqual(len(criacao.id), 10)

    def test_tamanho_maximo_raca(self):
        criacao = Criacao(id="123", raca="Labrador Retriever", data_entrada="2023-06-01")
        self.assertLessEqual(len(criacao.raca), 20)

    def test_elementos_obrigatorios(self):
        criacao = Criacao(id="123", raca="Cachorro", data_entrada="2023-06-01")
        self.assertIsNotNone(criacao.id)
        self.assertIsNotNone(criacao.raca)
        self.assertIsNotNone(criacao.data_entrada)

    def test_verbose_name(self):
        criacao = Criacao(id="123", raca="Cachorro", data_entrada="2023-06-01")
        self.assertEqual(criacao._meta.get_field('id').verbose_name, 'ID')
        self.assertEqual(criacao._meta.get_field('raca').verbose_name, 'Raça')
        self.assertEqual(criacao._meta.get_field('data_entrada').verbose_name, 'Data de Entrada')


class TestColeta(unittest.TestCase):
    def setUp(self):
        self.criacao = Criacao(id="123", raca="Cachorro", data_entrada="2023-06-01")

    def test_ordenacao_coletas(self):
        coleta1 = Coleta(id=1, criacao=self.criacao, data="2023-06-03", quantidade=5)
        coleta2 = Coleta(id=2, criacao=self.criacao, data="2023-06-02", quantidade=3)
        coleta3 = Coleta(id=3, criacao=self.criacao, data="2023-06-04", quantidade=2)

        coletas = [coleta1, coleta2, coleta3]
        coletas_ordenadas = sorted(coletas, key=lambda c: c.data, reverse=True)

        self.assertEqual(coletas_ordenadas, [coleta3, coleta1, coleta2])

class ListarColetasViewTest(TestCase):
    def setUp(self):
        self.url = reverse('listar_coletas')
        # Criar algumas instâncias de coletas para testar a listagem
        self.coleta1 = Coleta.objects.create(id=1, criacao=criacao, data="2023-06-01", quantidade=10)
        self.coleta2 = Coleta.objects.create(id=2, criacao=criacao, data="2023-06-02", quantidade=5)

    def test_url_correta(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'listar_coletas.html')

    def test_listar_todas_coletas(self):
        response = self.client.get(self.url)
        coletas = response.context['coletas']
        self.assertEqual(len(coletas), 2)
        self.assertIn(self.coleta1, coletas)
        self.assertIn(self.coleta2, coletas)


class DetalhesColetaViewTest(TestCase):
    def setUp(self):
        self.coleta = Coleta.objects.create(id=1, criacao=criacao, data="2023-06-01", quantidade=10)
        self.url = reverse('detalhes_coleta', args=[self.coleta.id])

    def test_url_correta(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'detalhes_coleta.html')

    def test_mostrar_detalhes_corretos(self):
        response = self.client.get(self.url)
        coleta = response.context['coleta']
        self.assertEqual(coleta, self.coleta)


class DeletarColetaViewTest(TestCase):
    def setUp(self):
        self.coleta = Coleta.objects.create(id=1, criacao=criacao, data="2023-06-01", quantidade=10)
        self.url = reverse('deletar_coleta', args=[self.coleta.id])

    def test_url_correta(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'deletar_coleta.html')

    def test_deletar_coleta_indicada(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Coleta.objects.filter(id=self.coleta.id).exists())

class ColetaFormTest(TestCase):
    def setUp(self):
        # Criar uma instância de Coleta para ser usada nos testes
        self.coleta = Coleta.objects.create(id=1, criacao=criacao, data="2023-06-01", quantidade=10)

    def test_formulario_criacao_coleta_valido(self):
        data = {
            'criacao': self.coleta.criacao.id,
            'data': '2023-06-02',
            'quantidade': 5,
        }
        form = ColetaForm(data=data)
        self.assertTrue(form.is_valid())

    def test_formulario_criacao_coleta_data_duplicada(self):
        data = {
            'criacao': self.coleta.criacao.id,
            'data': '2023-06-01',  # Mesma data da coleta existente
            'quantidade': 5,
        }
        form = ColetaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

    def test_formulario_criacao_coleta_data_futura(self):
        data = {
            'criacao': self.coleta.criacao.id,
            'data': '2023-07-01',  # Data futura
            'quantidade': 5,
        }
        form = ColetaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

    def test_formulario_edicao_coleta_valido(self):
        data = {
            'criacao': self.coleta.criacao.id,
            'data': '2023-06-02',
            'quantidade': 5,
        }
        form = ColetaForm(instance=self.coleta, data=data)
        self.assertTrue(form.is_valid())

    def test_formulario_edicao_coleta_data_duplicada(self):
        outra_coleta = Coleta.objects.create(id=2, criacao=criacao, data="2023-06-02", quantidade=5)
        data = {
            'criacao': self.coleta.criacao.id,
            'data': '2023-06-02',  # Mesma data de outra coleta existente
            'quantidade': 5,
        }
        form = ColetaForm(instance=self.coleta, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

    def test_formulario_edicao_coleta_data_futura(self):
        data = {
            'criacao': self.coleta.criacao.id,
            'data': '2023-07-01',  # Data futura
            'quantidade': 5,
        }
        form = ColetaForm(instance=self.coleta, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('data', form.errors)

class CriarColetaViewTest(TestCase):
    def setUp(self):
        self.url = reverse('criar_coleta')
        # Criar instância de Criacao para ser usada no formulário
        self.criacao = Criacao.objects.create(id=1, raca="Cachorro", data_entrada="2023-06-01")

    def test_url_correta(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'criar_coleta.html')

    def test_criar_coleta_objeto(self):
        data = {
            'criacao': self.criacao.id,
            'data': '2023-06-01',
            'quantidade': 10,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Coleta.objects.filter(criacao=self.criacao, data="2023-06-01", quantidade=10).exists())


class EditarColetaViewTest(TestCase):
    def setUp(self):
        self.coleta = Coleta.objects.create(id=1, criacao=criacao, data="2023-06-01", quantidade=10)
        self.url = reverse('editar_coleta', args=[self.coleta.id])

    def test_url_correta(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'editar_coleta.html')

    def test_editar_coleta_objeto(self):
        data = {
            'criacao': self.coleta.criacao.id,
            'data': '2023-06-02',
            'quantidade': 5,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.coleta.refresh_from_db()
        self.assertEqual(self.coleta.data, "2023-06-02")
        self.assertEqual(self.coleta.quantidade, 5)


class ExibirRelatorioColetaViewTest(TestCase):
    def setUp(self):
        self.url = reverse('exibir_relatorio_coleta')

    def test_url_correta(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template_correto(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'exibir_relatorio_coleta.html')

    def test_exibir_relatorio_corretamente(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('relatorio', response.context)
        relatorio = response.context['relatorio']
        self.assertIsNotNone(relatorio)
        # Verificar se o relatório possui a soma correta da quantidade coletada por mês nos últimos 12 meses
        # Você precisará implementar a lógica do relatório de acordo com os requisitos
        # e fazer as devidas asserções nos valores do relatório


if __name__ == '__main__':
    unittest.main()

