# Julia: tipos paramétricos y despacho múltiple.
struct Exposure{T<:AbstractFloat}
    pd::T
    lgd::T
    ead::T
    function Exposure(pd::T, lgd::T, ead::T) where {T<:AbstractFloat}
        all(isfinite, (pd, lgd, ead)) || throw(ArgumentError("No finito"))
        (0 <= pd <= 1 && 0 <= lgd <= 1 && ead >= 0) ||
            throw(ArgumentError("Parámetros fuera de dominio"))
        new{T}(pd, lgd, ead)
    end
end

expected_loss(xs::AbstractVector{<:Exposure}) =
    sum(x -> x.pd * x.lgd * x.ead, xs; init=0.0)

xs = [Exposure(0.02, 0.4, 1000.0),
      Exposure(0.05, 0.6, 2000.0),
      Exposure(0.10, 0.3, 500.0)]
result = expected_loss(xs)
@assert isapprox(result, 83.0; atol=1e-10)
println("EL=", round(result; digits=10))
