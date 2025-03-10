// Copyright 2024 RisingLight Project Authors. Licensed under Apache-2.0.

// Cada Classe de Equivalência é uma lista de expressões equivalentes
// Cada expressão é um nó no E-Graph e é equivalente a todas as outras expressões na mesma classe
// Temos prints para exibir o número de classes de equivalência e o número de expressões equivalentes em cada classe
// Faz-se várias iterações para otimizar a expressão, em cada iteração são aplicadas reescritas de regras

// Já conseguimos distinguir operadores relacionais de outros operadores

use std::sync::LazyLock;
use egg::CostFunction;
use csv::Writer;
use std::error::Error;
use std::path::Path;
use std::fs::{OpenOptions, create_dir_all};
use std::fs::File;
use std::io::{BufRead, BufReader};
use super::*;
use crate::catalog::RootCatalogRef;
use crate::planner::EGraph;
use std::collections::HashMap;

/// Plan optimizer.
#[derive(Clone)]
pub struct Optimizer {
    analysis: ExprAnalysis,
}

/// Optimizer configurations.
#[derive(Debug, Clone, Default)]
pub struct Config {
    pub enable_range_filter_scan: bool,
    pub table_is_sorted_by_primary_key: bool,
}


// Função para formatar um nó de forma legível
fn format_enode(enode: &Expr) -> String {
    match enode {
        Expr::Constant(value) => format!("Constant({:?})", value),
        Expr::Column(id) => format!("Column({:?})", id),
        Expr::Table(id) => format!("Table({:?})", id),
        Expr::Scan(children) => format!("Scan({:?})", children),
        Expr::Filter(children) => format!("Filter({:?})", children),
        Expr::Proj(children) => format!("Proj({:?})", children),
        Expr::HashAgg(children) => format!("HashAgg({:?})", children),
        Expr::Order(children) => format!("Order({:?})", children),
        Expr::Join(children) => format!("Join({:?})", children),
        Expr::Add(children) => format!("Add({:?})", children),
        Expr::Sub(children) => format!("Sub({:?})", children),
        Expr::Mul(children) => format!("Mul({:?})", children),
        Expr::Div(children) => format!("Div({:?})", children),
        Expr::Gt(children) => format!("Gt({:?})", children),
        Expr::Lt(children) => format!("Lt({:?})", children),
        Expr::Eq(children) => format!("Eq({:?})", children),
        Expr::And(children) => format!("And({:?})", children),
        Expr::Or(children) => format!("Or({:?})", children),
        Expr::Not(children) => format!("Not({:?})", children),
        Expr::List(children) => format!("List({:?})", children),
        Expr::Ref(id) => format!("Ref({:?})", id),
        _ => format!("{:?}", enode), // Caso padrão para outros nós
    }
}


// Função para visitar e enumerar as alternativas no E-Graph
fn visit_and_enumerate_alternatives(egraph: &EGraph) -> (usize, usize, usize, f64) {

    // Itera sobre todas as classes de equivalência no E-Graph
    let mut classes_eq = 0;
    let mut num_nodes;
    let mut class_nodes_map: HashMap<usize, Vec<String>> = HashMap::new();

    for (class_id, eclass) in egraph.classes().enumerate() {
        classes_eq += 1;
        num_nodes = 0;
        let mut nodes = Vec::new();
        
        // Itera sobre todos os nós na classe de equivalência
        for (_node_id, enode) in eclass.nodes.iter().enumerate() {
            num_nodes += 1;
            nodes.push(format!("{:?}", enode));
        }
        
        class_nodes_map.insert(class_id, nodes);
        println!("Classe {:>3} | Expressões: {:>2}\n", class_id, num_nodes);
    }

    // Calcular o valor mínimo, máximo e médio de expressões por classe
    let mut min_nodes = usize::MAX;
    let mut max_nodes = usize::MIN;
    let mut total_nodes = 0;

    for nodes in class_nodes_map.values() {
        let count = nodes.len();
        if count < min_nodes {
            min_nodes = count;
        }
        if count > max_nodes {
            max_nodes = count;
        }
        total_nodes += count;
    }

    let avg_nodes = if classes_eq > 0 {
        total_nodes as f64 / classes_eq as f64
    } else {
        0.0
    };

    println!("Mínimo: {}", min_nodes);
    println!("Máximo: {}", max_nodes);
    println!("Média: {:.2}", avg_nodes);

    (classes_eq, min_nodes, max_nodes, avg_nodes)
}



/// Função para garantir que a pasta exista antes de criar o ficheiro
fn ensure_directory_exists(file_path: &str) -> Result<(), Box<dyn Error>> {
    if let Some(parent) = Path::new(file_path).parent() {
        create_dir_all(parent)?;  // Cria o diretório se não existir
    }
    Ok(())
}

/// Função para escrever o cabeçalho do CSV
fn write_csv_header(file_path: &str) -> Result<(), Box<dyn Error>> {
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(file_path)?;
    let mut wtr = Writer::from_writer(file);

    wtr.write_record(&["Stage", "Custo", "Relacionais", "Classes_Total", "Min", "Max", "Media"])?;
    wtr.flush()?;
    Ok(())
}

/// Função para armazenar os dados no CSV
fn save_to_csv(
    stage: &str, 
    custo: f32, 
    relacionais: usize, 
    classes_total: usize,
    min: usize,
    max: usize,
    media: f64,
    base_name: &str
) -> Result<String, Box<dyn Error>> {
    ensure_directory_exists(base_name)?;

    // Se o arquivo não existe, escreve o cabeçalho
    if !Path::new(base_name).exists() {
        write_csv_header(base_name)?;
    }

    let file = OpenOptions::new()
        .append(true)
        .create(true)
        .open(base_name)?;
    let mut wtr = Writer::from_writer(file);

    // Escreve os dados em uma única linha
    wtr.write_record(&[
        stage.to_string(),
        custo.to_string(),
        relacionais.to_string(),
        classes_total.to_string(),
        min.to_string(),
        max.to_string(),
        format!("{:.2}", media)
    ])?;
    wtr.flush()?;

    Ok(base_name.to_string())
}

// Função para identificar operadores relacionais e contar
fn detail_expr(expr: &RecExpr) -> usize {
    let lista_relacionais = [
        "Join", "Filter", "Proj", "HashAgg", "Order", "Scan",
        "HashJoin", "IndexScan", "SeqScan", "MergeJoin",
        "Values", "TopN",
    ];

    let mut counter = 0;
    for n in expr.as_ref().iter().map(|n| format_enode(n)) {
        if let Some(first_element) = n.split('(').next() {
            if lista_relacionais.contains(&first_element) {
                counter += 1;
            }
        }
    }
    println!("Relacionais: {}", counter);

    counter
}



impl Optimizer {
    pub fn new(catalog: RootCatalogRef, stat: Statistics, config: Config) -> Self {
        Self {
            analysis: ExprAnalysis {
                catalog,
                config,
                stat,
            },
        }
    }

    pub fn optimize(&self, mut expr: RecExpr) -> RecExpr {
        let mut cost = f32::MAX;

        // Faz-se aqui a leitura do ficheiro temporário para garantir que o ficheiro já tem o path certo
        // Caminho do ficheiro temporário
        let temp_file_path = "temp_file_path.txt";

        // Ler o caminho do arquivo do ficheiro temporário
        let file = File::open(temp_file_path).expect("Falha ao abrir o ficheiro temporário");
        let reader = BufReader::new(file);

        // Ler a primeira linha (que contém o caminho do arquivo)
        let file_path = reader.lines().next().expect("Ficheiro temporário vazio").expect("Falha ao ler a linha");

        // Usar o caminho do arquivo
        let path = Path::new(&file_path);
        let file_stem = path.file_stem().unwrap_or_default().to_string_lossy();
        let output_file = format!("src/planner/outputs/query_data/{}_data.csv", file_stem);
        
        // Criar o diretório se não existir
        if let Some(parent) = Path::new(&output_file).parent() {
            create_dir_all(parent).expect("Failed to create output directory");
        }

        println!("Ficheiro de entrada: {}", file_path);
        println!("Ficheiro de saída: {}", output_file);

        // 0. stage inicial (pré-otimização)
        let mut egraph = EGraph::new(self.analysis.clone());
        egraph.add_expr(&expr);
        println!("Stage 0\n");
        let relacionais = detail_expr(&expr);
        let (classes_eq, min_nodes, max_nodes, avg_nodes) = visit_and_enumerate_alternatives(&egraph);
        println!("Classes-Total {}\n", classes_eq);
        println!("\nCustoI: {}", cost);
        
        save_to_csv(
            "0",
            cost,
            relacionais,
            classes_eq,
            min_nodes,
            max_nodes,
            avg_nodes,
            &output_file,
        ).expect("Falha ao salvar no CSV");

        // 1. pushdown apply 
        println!("\nStage 1\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE1_RULES.iter(), 2, 6);
        println!("Custo1: {}", cost);
        let relacionais = detail_expr(&expr);
        let (classes_eq, min_nodes, max_nodes, avg_nodes) = visit_and_enumerate_alternatives(&egraph);
        println!("Classes-Total {}\n", classes_eq);
        save_to_csv(
            "1",
            cost,
            relacionais,
            classes_eq,
            min_nodes,
            max_nodes,
            avg_nodes,
            &output_file,
        ).expect("Falha ao salvar no CSV");


        // 2. pushdown predicate and projection
        println!("\nStage 2\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE2_RULES.iter(), 4, 6);
        println!("Custo2: {}", cost);
        let relacionais = detail_expr(&expr);
        let (classes_eq, min_nodes, max_nodes, avg_nodes) = visit_and_enumerate_alternatives(&egraph);
        println!("Classes-Total {}\n", classes_eq);
        save_to_csv(
            "2",
            cost,
            relacionais,
            classes_eq,
            min_nodes,
            max_nodes,
            avg_nodes,
            &output_file,
        ).expect("Falha ao salvar no CSV");


        // 3. join reorder and hashjoin
        println!("\nStage 3\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE3_RULES.iter(), 3, 8);
        println!("Custo3: {}", cost);
        let relacionais = detail_expr(&expr);
        let (classes_eq, min_nodes, max_nodes, avg_nodes) = visit_and_enumerate_alternatives(&egraph);
        println!("Classes-Total {}\n", classes_eq);
        save_to_csv(
            "3",
            cost,
            relacionais,
            classes_eq,
            min_nodes,
            max_nodes,
            avg_nodes,
            &output_file,
        ).expect("Falha ao salvar no CSV");

        println!("\n\nResultados guardados em '{}'", &output_file);

        expr
    }



    /// Optimize the expression with the given rules in multiple iterations.
    /// In each iteration, the best expression is selected as the input of the next iteration.
    fn optimize_stage<'a>(
        &self,
        expr: &mut RecExpr,
        cost: &mut f32,
        rules: impl IntoIterator<Item = &'a Rewrite> + Clone,
        iteration: usize,
        iter_limit: usize,
    ) {
        for i in 0..iteration {
            println!("\nIteração: {}\n ", i);
            let runner = egg::Runner::<_, _, ()>::new(self.analysis.clone())
                .with_expr(expr)
                .with_iter_limit(iter_limit)
                .run(rules.clone());
                        
            let cost_fn = cost::CostFn {
                egraph: &runner.egraph,
            };
            let extractor = egg::Extractor::new(&runner.egraph, cost_fn);
            let cost0;
            (cost0, *expr) = extractor.find_best(runner.roots[0]);
            
            *cost = cost0;
        }
    }

    /// Returns the cost for each node in the expression.
    pub fn costs(&self, expr: &RecExpr) -> Vec<f32> {
        let mut egraph = EGraph::new(self.analysis.clone());
        // NOTE: we assume Expr node has the same Id in both EGraph and RecExpr.
        egraph.add_expr(expr);
        let mut cost_fn = cost::CostFn { egraph: &egraph };
        let mut costs = vec![0.0; expr.as_ref().len()];
        for (i, node) in expr.as_ref().iter().enumerate() {
            let cost = cost_fn.cost(node, |i| costs[usize::from(i)]);
            costs[i] = cost;
        }
        costs
    }

    /// Returns the estimated row for each node in the expression.
    pub fn rows(&self, expr: &RecExpr) -> Vec<f32> {
        let mut egraph = EGraph::new(self.analysis.clone());
        // NOTE: we assume Expr node has the same Id in both EGraph and RecExpr.
        egraph.add_expr(expr);
        (0..expr.as_ref().len())
            .map(|i| egraph[i.into()].data.rows)
            .collect()
    }

    /// Returns the catalog.
    pub fn catalog(&self) -> &RootCatalogRef {
        &self.analysis.catalog
    }
}

/// Stage1 rules in the optimizer.
/// - pushdown apply and turn into join
static STAGE1_RULES: LazyLock<Vec<Rewrite>> = LazyLock::new(|| {
    let mut rules = vec![];
    rules.append(&mut rules::expr::and_rules());
    rules.append(&mut rules::plan::always_better_rules());
    rules.append(&mut rules::plan::subquery_rules());
    rules
});

/// Stage2 rules in the optimizer.
/// - pushdown predicate, projection, and index scan
static STAGE2_RULES: LazyLock<Vec<Rewrite>> = LazyLock::new(|| {
    let mut rules = vec![];
    rules.append(&mut rules::expr::rules());
    rules.append(&mut rules::plan::always_better_rules());
    rules.append(&mut rules::plan::predicate_pushdown_rules());
    rules.append(&mut rules::plan::projection_pushdown_rules());
    rules.append(&mut rules::plan::index_scan_rules());
    rules
});

/// Stage3 rules in the optimizer.
/// - join reorder and hashjoin
static STAGE3_RULES: LazyLock<Vec<Rewrite>> = LazyLock::new(|| {
    let mut rules = vec![];
    rules.append(&mut rules::expr::and_rules());
    rules.append(&mut rules::plan::always_better_rules());
    rules.append(&mut rules::plan::join_reorder_rules());
    rules.append(&mut rules::plan::hash_join_rules());
    rules.append(&mut rules::plan::predicate_pushdown_rules());
    rules.append(&mut rules::plan::projection_pushdown_rules());
    rules.append(&mut rules::order::order_rules());
    rules
});

