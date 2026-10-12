# R base: validación y cálculo vectorizado de pérdida esperada.
expected_loss <- function(pd, lgd, ead) {
  stopifnot(is.numeric(pd), is.numeric(lgd), is.numeric(ead))
  stopifnot(length(pd) == length(lgd), length(pd) == length(ead))
  stopifnot(all(is.finite(pd)), all(is.finite(lgd)), all(is.finite(ead)))
  stopifnot(all(pd >= 0 & pd <= 1), all(lgd >= 0 & lgd <= 1), all(ead >= 0))
  sum(pd * lgd * ead)
}

pd <- c(0.02, 0.05, 0.10)
lgd <- c(0.4, 0.6, 0.3)
ead <- c(1000, 2000, 500)
result <- expected_loss(pd, lgd, ead)
stopifnot(isTRUE(all.equal(result, 83.0, tolerance = 1e-10)))
cat(sprintf("EL=%.10f\n", result))
