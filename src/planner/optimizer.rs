// Copyright 2024 RisingLight Project Authors. Licensed under Apache-2.0.

// Cada Classe de Equivalência é uma lista de expressões equivalentes
// Cada expressão é um nó no E-Graph e é equivalente a todas as outras expressões na mesma classe
// Temos prints para exibir o número de classes de equivalência e o número de expressões equivalentes em cada classe
// Faz-se várias iterações para otimizar a expressão, em cada iteração são aplicadas reescritas de regras

use std::sync::LazyLock;
use egg::Language;
use egg::CostFunction;
use egg::Id;

use super::*;
use crate::catalog::RootCatalogRef;
use crate::planner::EGraph;

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
fn visit_and_enumerate_alternatives(egraph: &EGraph) -> usize {
    // Itera sobre todas as classes de equivalência no E-Graph
    
    let mut classes_eq = 0;
    let mut num_nodes = 0;

    for (class_id, eclass) in egraph.classes().enumerate() {
        classes_eq += 1;
        num_nodes = 0;
        // Itera sobre todos os nós na classe de equivalência
        for (node_id, enode) in eclass.nodes.iter().enumerate() {
            num_nodes += 1;
            //println!("\nNó Número {:?}    Nó Info: {:?}   Filhos: {:?}\n", node_id, enode, enode.children().len());
        }
        println!("\nClasse {:?} Nº de Exprs Equivalentes: {:?}\n", class_id, num_nodes);
    }
    classes_eq
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

        // Define extra rules for some configurations
        let mut extra_rules = vec![];
        if self.analysis.config.enable_range_filter_scan {
            extra_rules.append(&mut rules::range::filter_scan_rule());
        }

        let root_id = Id::from(expr.as_ref().len() - 1);

        println!("\nCusto inicial: {}", cost);

        // 1. pushdown apply
        println!("\n----------------------- Stage 1 ------------------------------\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE1_RULES.iter(), 2, 6);
        let root_id = Id::from(expr.as_ref().len() - 1);
        println!("Custo atual: {}", cost);
        
        // 2. pushdown predicate and projection
        println!("\n----------------------- Stage 2 ------------------------------\n");
        let rules = STAGE2_RULES.iter().chain(&extra_rules);
        self.optimize_stage(&mut expr, &mut cost, rules, 4, 6);
        let root_id = Id::from(expr.as_ref().len() - 1);
        println!("Custo atual: {}", cost);

        // 3. join reorder and hashjoin
        println!("\n----------------------- Stage 3 ------------------------------\n");
        self.optimize_stage(&mut expr, &mut cost, STAGE3_RULES.iter(), 3, 8);
        let root_id = Id::from(expr.as_ref().len() - 1);
        println!("Custo final: {}", cost);
        

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
        let mut eqs = 0;

        for i in 0..iteration {
            println!("\n ^^^^ Stage atual - Iteração: {} ^^^^\n ", i);
            let runner = egg::Runner::<_, _, ()>::new(self.analysis.clone())
                .with_expr(expr)
                .with_iter_limit(iter_limit)
                .run(rules.clone());
    
            // Visita e enumera as alternativas no E-Graph
            eqs = visit_and_enumerate_alternatives(&runner.egraph);
                        
            let cost_fn = cost::CostFn {
                egraph: &runner.egraph,
            };
            let extractor = egg::Extractor::new(&runner.egraph, cost_fn);
            let cost0;
            (cost0, *expr) = extractor.find_best(runner.roots[0]);
            
            *cost = cost0;
        }
        println!("\nNúmero total de classes de equivalência: {}\n", eqs);
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
