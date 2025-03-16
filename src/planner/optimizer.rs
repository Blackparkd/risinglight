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

#[derive(Debug)]
struct ClassInfo {
    class_id: usize,
    node_count: usize,
    nodes: Vec<String>
}

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
fn visit_and_enumerate_alternatives(egraph: &EGraph) -> (usize, usize, usize, f64, Vec<ClassInfo>) {
    let mut classes_eq = 0;
    let mut class_infos = Vec::new();

    for (class_id, eclass) in egraph.classes().enumerate() {
        classes_eq += 1;
        let mut nodes = Vec::new();
        
        // Collect nodes in this class
        for (_node_id, enode) in eclass.nodes.iter().enumerate() {
            nodes.push(format!("{:?}", enode));
        }
        
        class_infos.push(ClassInfo {
            class_id,
            node_count: nodes.len(),
            nodes,
        });
    }

    // Calculate statistics as before
    let mut min_nodes = usize::MAX;
    let mut max_nodes = usize::MIN;
    let mut total_nodes = 0;

    for info in &class_infos {
        let count = info.node_count;
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

    (classes_eq, min_nodes, max_nodes, avg_nodes, class_infos)
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
    // Use absolute path
    let abs_path = std::env::current_dir()?.join(base_name);
    let abs_path_str = abs_path.to_str().ok_or("Invalid path")?;
    
    // Ensure directory exists
    if let Some(parent) = abs_path.parent() {
        create_dir_all(parent)?;
    }

    // Create or append to file with explicit drop
    {
        let file = OpenOptions::new()
            .write(true)
            .create(true)
            .append(true)
            .open(&abs_path)?;
        
        let mut wtr = Writer::from_writer(file);

        // Write header if file is empty
        if abs_path.metadata()?.len() == 0 {
            wtr.write_record(&["Stage", "Custo", "Relacionais", "Classes_Total", "Min", "Max", "Media"])?;
        }

        // Write data
        wtr.write_record(&[
            stage.to_string(),
            custo.to_string(),
            relacionais.to_string(),
            classes_total.to_string(),
            min.to_string(),
            max.to_string(),
            format!("{:.2}", media)
        ])?;
        
        // Explicit flush and drop
        wtr.flush()?;
    } // File handle is explicitly dropped here

    Ok(abs_path_str.to_string())
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

fn save_class_details(
    stage: &str,
    class_infos: &[ClassInfo],
    base_name: &str
) -> Result<String, Box<dyn Error>> {
    // Get the base filename without path and extension
    let base_filename = Path::new(base_name)
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .trim_end_matches(".csv")
        .to_string();
    
    // Extract query number (assuming filename format like "q1_data")
    let query_dir = if let Some(query_num) = base_filename.split('_').next() {
        query_num
    } else {
        "unknown_query"
    };
    
    // Create output directory path for this specific query
    let output_dir = Path::new("src/planner/outputs/data_classes").join(query_dir);
    
    // Ensure directory exists
    create_dir_all(&output_dir)?;
    
    // Create the new file path in the query-specific directory
    let detailed_file = output_dir.join(format!("stage_{}_classes.csv", stage));

    println!("Saving class details to: {}", detailed_file.display());

    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(&detailed_file)?;
    
    let mut wtr = Writer::from_writer(file);

    // Write header
    wtr.write_record(&["Stage", "Class_ID", "Node_Count", "Nodes"])?;

    // Write data for each class
    for info in class_infos {
        wtr.write_record(&[
            stage.to_string(),
            info.class_id.to_string(),
            info.node_count.to_string(),
            info.nodes.join("; ")
        ])?;
    }

    wtr.flush()?;
    Ok(detailed_file.to_string_lossy().into_owned())
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

        // 0. stage inicial (pré-otimização)
        let mut egraph = EGraph::new(self.analysis.clone());
        egraph.add_expr(&expr);
        println!("Stage 0\n");
        let relacionais = detail_expr(&expr);
        let (classes_eq, min_nodes, max_nodes, avg_nodes, class_infos) = visit_and_enumerate_alternatives(&egraph);
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

        save_class_details("0", &class_infos, &output_file).expect("Falha ao salvar detalhes das classes no CSV");

        // 1. pushdown apply 
        println!("\nStage 1\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE1_RULES.iter(), 2, 6, "1", &output_file);

        // 2. pushdown predicate and projection
        println!("\nStage 2\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE2_RULES.iter(), 4, 6, "2", &output_file);

        // 3. join reorder and hashjoin
        println!("\nStage 3\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE3_RULES.iter(), 3, 8, "3", &output_file);

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
        stage: &str,
        output_file: &str,
    ) {
        for _i in 0..iteration {
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

            // Get detailed class information
            let (classes_eq, min_nodes, max_nodes, avg_nodes, class_infos) = 
                visit_and_enumerate_alternatives(&runner.egraph);

            // Save regular statistics
            let relacionais = detail_expr(expr);
            save_to_csv(
                stage,
                *cost,
                relacionais,
                classes_eq,
                min_nodes,
                max_nodes,
                avg_nodes,
                output_file,
            ).expect("Falha ao salvar no CSV");

            // Save detailed class information
            save_class_details(
                stage,
                &class_infos,
                output_file,
            ).expect("Falha ao salvar detalhes das classes");
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

