// Copyright 2024 RisingLight Project Authors. Licensed under Apache-2.0.

// Cada Classe de Equivalência é uma lista de expressões equivalentes
// Cada expressão é um nó no E-Graph e é equivalente a todas as outras expressões na mesma classe
// Temos prints para exibir o número de classes de equivalência e o número de expressões equivalentes em cada classe
// Faz-se várias iterações para otimizar a expressão, em cada iteração são aplicadas reescritas de regras

// Já conseguimos distinguir operadores relacionais de outros operadores

// ToDo: Fazer relatório:
// Acrescentar queries do tpch
// Falar sobre o optimizer: queries simples
// Falar sobre o custo: como é que se calcula, o que é que influencia
// Falar sobre o número de classes de equivalência e o número de expressões equivalentes em cada classe
// Falar sobre o número de merges do egg


use std::sync::LazyLock;
use egg::CostFunction;
use csv::Writer;
use std::error::Error;
use std::path::Path;
use std::fs::{OpenOptions, create_dir_all};
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::fs;
use super::*;
use crate::catalog::RootCatalogRef;
use crate::planner::EGraph;
use std::io::Write;

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

// =============================== MY HELPERS - START ==================================================== //

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

    // Calcular estatísticas
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

// Função para salvar detalhes das classes
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

// Função para salvar o número de merges do Egg
fn save_egg_merges(
    stage: &str,
    merge_count: usize,
    hc_size: usize,
    n_classes: usize,
    base_name: &str
) -> Result<String, Box<dyn Error>> {
    let path = Path::new(base_name);
    let file_stem = path.file_stem().unwrap_or_default().to_string_lossy();
    let output_dir = format!("src/planner/outputs/egg-merges/{}", file_stem);
    create_dir_all(&output_dir)?;

    let output_path = format!("{}/egg_merges.csv", output_dir);
    let file_exists = Path::new(&output_path).exists();

    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .append(true)
        .open(&output_path)?;

    let mut wtr = Writer::from_writer(file);

    // Novo cabeçalho
    if !file_exists {
        wtr.write_record(&["Stage", "Merge_Count", "HC_Size", "Num_Classes"])?;
    }

    // Nova linha de dados
    wtr.write_record(&[
        stage,
        &merge_count.to_string(),
        &hc_size.to_string(),
        &n_classes.to_string(),
    ])?;

    wtr.flush()?;
    println!("✅ Egg merge count and sizes saved to: {}", output_path);
    Ok(output_path)
}

// Função para salvar os dados de aplicação de regras (apenas na última iteração)
fn save_rules_data(
    stage: &str,
    runner: &egg::Runner<Expr, ExprAnalysis, ()>,
    output_file_base: &str
) -> Result<(), Box<dyn std::error::Error>> {
    // Extrair o nome da consulta do caminho do arquivo base
    let path = Path::new(output_file_base);
    let file_stem = path.file_stem().unwrap_or_default().to_string_lossy();
    
    // Criar o diretório para os dados de regras se não existir
    let output_dir = format!("src/planner/outputs/rules_data/{}", file_stem);
    create_dir_all(&output_dir)?;
    
    // Caminho para o arquivo CSV de saída
    let output_path = format!("{}/stage_{}_rules_application.csv", output_dir, stage);
    
    // Abrir o arquivo CSV para escrita
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(&output_path)?;
    
    let mut wtr = Writer::from_writer(file);
    
    // Escrever cabeçalhos
    wtr.write_record(&[
        "Stage", 
        "Internal_Iteration",  // Iteração interna (do runner)
        "Class_Count", 
        "Node_Count",
        "Rule_Name", 
        "Applications"
    ])?;
    
    // Para cada iteração interna, escrever as regras aplicadas
    for (iter_idx, iter_data) in runner.iterations.iter().enumerate() {
        // Usar os campos corretos disponíveis no tipo Iteration<()>
        let class_count = iter_data.egraph_classes;
        let node_count = iter_data.egraph_nodes;
        
        // Para cada regra aplicada nesta iteração
        for applied in &iter_data.applied {
            wtr.write_record(&[
                stage,
                &iter_idx.to_string(),
                &class_count.to_string(),
                &node_count.to_string(),
                &applied.0.to_string(), // Nome da regra
                &applied.1.to_string()  // Número de aplicações
            ])?;
        }
        
        // Se não houver regras aplicadas nesta iteração, ainda registra a iteração
        if iter_data.applied.is_empty() {
            wtr.write_record(&[
                stage,
                &iter_idx.to_string(),
                &class_count.to_string(),
                &node_count.to_string(),
                "None",
                "0"
            ])?;
        }
    }
    
    // Garantir que os dados sejam gravados
    wtr.flush()?;
    
    println!("✅ Rules application data saved to: {}", output_path);
    Ok(())
}

/// Função para analisar e salvar estatísticas sobre quais regras foram mais aplicadas
fn analyze_and_save_rule_statistics(
    stage: &str,
    runner: &egg::Runner<Expr, ExprAnalysis, ()>,
    output_file_base: &str
) -> Result<(), Box<dyn std::error::Error>> {
    // Extrair o nome da consulta do caminho do arquivo base
    let path = Path::new(output_file_base);
    let file_stem = path.file_stem().unwrap_or_default().to_string_lossy();
    
    // Criar o diretório para os dados de regras se não existir
    let output_dir = format!("src/planner/outputs/rules_stats/{}", file_stem);
    create_dir_all(&output_dir)?;
    
    // Caminho para o arquivo CSV de saída
    let output_path = format!("{}/stage_{}_rule_stats.csv", output_dir, stage);
    
    // Coletar estatísticas agregadas sobre aplicações de regras
    let mut rule_applications: std::collections::HashMap<String, usize> = std::collections::HashMap::new();
    
    // Somar todas as aplicações de regras em todas as iterações
    for iter_data in &runner.iterations {
        for applied in &iter_data.applied {
            let rule_name = applied.0.to_string();
            let count = applied.1;
            *rule_applications.entry(rule_name).or_insert(0) += count;
        }
    }
    
    // Converter para um vetor e ordenar por número de aplicações (decrescente)
    let mut rule_stats: Vec<(String, usize)> = rule_applications.into_iter().collect();
    rule_stats.sort_by(|a, b| b.1.cmp(&a.1));
    
    // Abrir o arquivo CSV para escrita
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(&output_path)?;
    
    let mut wtr = Writer::from_writer(file);
    
    // Escrever cabeçalhos
    wtr.write_record(&["Stage", "Rule_Name", "Total_Applications", "Rank"])?;
    
    // Escrever dados ordenados
    for (rank, (rule_name, applications)) in rule_stats.iter().enumerate() {
        wtr.write_record(&[
            stage,
            rule_name,
            &applications.to_string(),
            &(rank + 1).to_string()
        ])?;
    }
    
    // Garantir que os dados sejam gravados
    wtr.flush()?;
    
    println!("✅ Rule statistics saved to: {}", output_path);
    
    // Se é o Stage 3, imprimir as 5 regras mais aplicadas
    if stage == "3" {
        println!("\n🔍 Top 5 regras mais aplicadas no Stage 3:");
        for (i, (rule_name, count)) in rule_stats.iter().take(5).enumerate() {
            println!("   {}. {} - {} aplicações", i+1, rule_name, count);
        }
        println!("");
    }
    
    Ok(())
}

// Função para calcular o custo total por estágio e salvar em CSV
fn calculate_and_save_total_costs(query_name: &str, stage_costs: &[f32]) -> Result<(), Box<dyn Error>> {
    // Criar o diretório se não existir
    let output_dir = Path::new("src/planner/outputs/total_costs");
    fs::create_dir_all(output_dir)?;
    
    // Nome do arquivo para salvar o custo total
    let output_file = output_dir.join(format!("{}_data_total_cost.csv", query_name));
    
    // Abrir arquivo para escrita
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(&output_file)?;
    
    let mut wtr = Writer::from_writer(file);
    
    // Escrever cabeçalho
    let mut headers = vec![String::from("Query")];  // Mudança aqui: String em vez de &str
    for i in 0..stage_costs.len() {
        headers.push(format!("Stage_{}_Cost", i+1));  // Mudança aqui: sem &
    }
    headers.push(String::from("Total_Cost"));  // Mudança aqui: String em vez de &str
    wtr.write_record(&headers)?;  // Não precisamos mudar aqui pois &[String] é convertido para &[&str] automaticamente
    
    // Calcular custo total
    let total_cost: f32 = stage_costs.iter().sum();
    
    // Preparar dados para escrita
    let mut row = vec![query_name.to_string()];
    for cost in stage_costs {
        row.push(cost.to_string());
    }
    row.push(total_cost.to_string());
    
    // Escrever linha com os dados
    wtr.write_record(&row)?;
    
    // Garantir que os dados sejam gravados
    wtr.flush()?;
    
    println!("✅ Total cost data saved to: {}", output_file.display());
    Ok(())
}

// Função para guardar a expressão relacional de cada stage num CSV
fn save_stage_expression(
    stage: &str,
    expr: &RecExpr,
    output_file: &str,
) -> Result<String, Box<dyn Error>> {
    use std::path::Path;

    // Extrair o nome da query do ficheiro base
    let base_filename = Path::new(output_file)
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .trim_end_matches(".csv")
        .to_string();

    // Extrair o número da query (ex: "q2")
    let query_dir = if let Some(query_num) = base_filename.split('_').next() {
        query_num
    } else {
        "unknown_query"
    };

    // Criar diretório para as expressões desta query
    let output_dir = Path::new("src/planner/outputs/expressions").join(query_dir);
    create_dir_all(&output_dir)?;

    // Caminho para o ficheiro CSV
    let csv_path = output_dir.join("expressions.csv");

    // Verificar se o ficheiro já existe para escrever o cabeçalho só uma vez
    let file_exists = csv_path.exists();

    let mut file = OpenOptions::new()
        .write(true)
        .create(true)
        .append(true)
        .open(&csv_path)?;

    // Escrever cabeçalho se o ficheiro for novo
    if !file_exists {
        writeln!(file, "Stage,Expression")?;
    }

    // Escrever a expressão (como string única, escapando aspas)
    let expr_str = format!("{:?}", expr).replace('"', "\"\"");
    writeln!(file, "{},\"{}\"", stage, expr_str)?;

    Ok(csv_path.to_string_lossy().into_owned())
}


/// Função para adicionar estatísticas sobre quais regras foram mais aplicadas ao final do arquivo
fn append_rule_statistics(
    stage: &str,
    runner: &egg::Runner<Expr, ExprAnalysis, ()>,
    output_file_base: &str
) -> Result<(), Box<dyn std::error::Error>> {
    // Extrair o nome da consulta do caminho do arquivo base
    let path = Path::new(output_file_base);
    let file_stem = path.file_stem().unwrap_or_default().to_string_lossy();

    // Criar o diretório para os dados de regras se não existir
    let output_dir = format!("src/planner/outputs/rules_stats/{}", file_stem);
    create_dir_all(&output_dir)?;

    // Caminho para o arquivo CSV de saída
    let output_path = format!("{}/stage_{}_rule_stats.csv", output_dir, stage);

    // Coletar estatísticas agregadas sobre aplicações de regras
    let mut rule_applications: std::collections::HashMap<String, usize> = std::collections::HashMap::new();

    // Somar todas as aplicações de regras em todas as iterações
    for iter_data in &runner.iterations {
        for applied in &iter_data.applied {
            let rule_name = applied.0.to_string();
            let count = applied.1;
            *rule_applications.entry(rule_name).or_insert(0) += count;
        }
    }

    // Converter para um vetor e ordenar por número de aplicações (decrescente)
    let mut rule_stats: Vec<(String, usize)> = rule_applications.into_iter().collect();
    rule_stats.sort_by(|a, b| b.1.cmp(&a.1));

    // Abrir o arquivo CSV para escrita (modo de adição)
    let file = OpenOptions::new()
        .write(true)
        .create(true)
        .append(true) // Adicionar ao final do arquivo
        .open(&output_path)?;

    let mut wtr = Writer::from_writer(file);

    // Escrever cabeçalhos apenas se o arquivo estiver vazio
    if Path::new(&output_path).metadata()?.len() == 0 {
        wtr.write_record(&["Stage", "Rule_Name", "Total_Applications", "Rank"])?;
    }

    // Escrever dados ordenados
    for (rank, (rule_name, applications)) in rule_stats.iter().enumerate() {
        wtr.write_record(&[
            stage,
            rule_name,
            &applications.to_string(),
            &(rank + 1).to_string()
        ])?;
    }

    // Garantir que os dados sejam gravados
    wtr.flush()?;

    println!("✅ Rule statistics appended to: {}", output_path);

    Ok(())
}



// =============================== MY HELPERS - END ==================================================== //

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
        let mut stage_costs = Vec::new(); // Armazenar os custos de cada estágio

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
        let context_file = file_path.clone(); // Definir context_file aqui
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
        

        //== SAVE ALL DATA ON CSV HERE ==//
        save_to_csv("0", cost, relacionais, classes_eq, min_nodes, max_nodes, avg_nodes, &output_file).expect("Falha ao guardar no CSV");
        save_class_details("0", &class_infos, &output_file).expect("Falha ao guardar os detalhes das classes no CSV");
        save_egg_merges("0", egraph.get_merge_count(), egraph.total_size(), egraph.number_of_classes(), &output_file).expect("Falha ao guardar contador de merges no CSV");
        save_stage_expression("0", &expr, &output_file).expect("Falha ao guardar expressão inicial no CSV");
        //===============================//

        // 1. pushdown apply 
        println!("\nStage 1\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE1_RULES.iter(), 2, 6, "1", &output_file, &file_stem);

        // 2. pushdown predicate and projection
        println!("\nStage 2\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE2_RULES.iter(), 4, 6, "2", &output_file, &file_stem);

        // 3. join reorder and hashjoin
        println!("\nStage 3\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE3_RULES.iter(), 3, 8, "3", &output_file, &file_stem);

        // Extrair o nome da query do arquivo de contexto atual
        let query_name = {
            let path = Path::new(&context_file);
            path.file_stem().unwrap_or_default().to_string_lossy().to_string()
        };
        
        // Salvar custos totais
        calculate_and_save_total_costs(&query_name, &stage_costs)
            .expect("Falha ao salvar custos totais");

        println!("\nSaving query information to: '{}'", &output_file);

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
        file_stem: &str, // Adicionado
    ) {
        // printing expression
        println!("Stage {}: {}", stage, expr);
        println!("Cost: {}", cost);

        for i in 0..iteration {
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

            // Apenas guarda os dados na última iteração
            if i == iteration - 1 {
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
                )
                .expect("Falha ao salvar no CSV");

                // Save detailed class information
                save_class_details(stage, &class_infos, output_file)
                    .expect("Falha ao salvar detalhes das classes");

                // Save rules application data
                save_rules_data(stage, &runner, output_file)
                    .expect("Falha ao guardar dados de aplicação de regras");

                // Para ir buscar ao Egg o número de merges para esta última iteration
                let merge_count = runner.egraph.get_merge_count();
                let hc_size = runner.egraph.total_size();
                let n_classes = runner.egraph.number_of_classes();
                println!("COUNTER MERGES: {}", merge_count);
                println!("HC SIZE: {}", hc_size);
                println!("NUM CLASSES: {}", n_classes);
                save_egg_merges(stage, merge_count, hc_size, n_classes, output_file)
                    .expect("Falha ao guardar contador de merges e tamanhos");

                // Save the final expression
                save_stage_expression(stage, expr, output_file)
                    .expect("Falha ao guardar expressão final");

                // Chamar a função de análise de regras com base na query
                if file_stem.starts_with("q15") {
                    println!(
                        "⚠️ Query 15 detected. Appending rule statistics for stage {}.",
                        stage
                    );
                    append_rule_statistics(stage, &runner, output_file)
                        .expect("Falha ao adicionar estatísticas de regras");
                } else {
                    analyze_and_save_rule_statistics(stage, &runner, output_file)
                        .expect("Falha ao analisar estatísticas de regras");
                }
            }
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

