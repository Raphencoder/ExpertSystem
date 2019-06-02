abstract type Op end

struct And <: Op end
struct Xor <: Op end
struct Or <: Op end
struct Not <: Op end
struct Letter <: Op end

struct Rule{T<:Op}
    A::Union{Rule, AbstractString}
    B::Union{Rule, Nothing}
    Rule{T}(A, B) where T <: Op = new{T}(A, B)
    Rule(A::AbstractString) = Rule{Letter}(A, nothing)
    function Rule{T}(before::AbstractString, after::AbstractString, index::Integer) where T <: Op
        Rule{T}(get_rule(before, index), get_rule(after, index))
    end
    function Rule{T}(str::AbstractString, index::Integer) where T <: Op
        Rule{T}(get_rule(str, index), nothing)
    end
end

Base.show(io::IO, e::Rule{And}) = print(io, "($(e.A) + $(e.B))")
Base.show(io::IO, e::Rule{Or})  = print(io, "($(e.A) | $(e.B))")
Base.show(io::IO, e::Rule{Xor}) = print(io, "($(e.A) ^ $(e.B))")
Base.show(io::IO, e::Rule{Not}) = print(io, "!$(e.A)")
Base.show(io::IO, e::Rule{Letter}) = print(io, e.A)

include("Parsing.jl")

function myerror(msg::AbstractString)
    @error msg
    exit(-1)
end

const op_type = Dict(
    '+' => And,
    '|' => Or,
    '^' => Xor
)

letters = Dict()
inputs = nothing
outputs = nothing
verbose = false

function parse_file(file)
    global letters = Dict()
    if !isfile(file)
        myerror("File does not exist")
    end
    open(file; read=true) do io
        index = 0
        for line in eachline(io)
            index += 1
            if (line = clean_line(line)) != nothing
                split_line(line, index)
            end
        end
        if isnothing(outputs) || isnothing(inputs)
            myerror("No input or no output")
        end
    end
end

solve(r::Rule{And}, letter) = solve(r.A, letter) && solve(r.B, letter)
solve(r::Rule{Or},  letter) = solve(r.A, letter) || solve(r.B, letter)
solve(r::Rule{Xor}, letter) = solve(r.A, letter) ⊻  solve(r.B, letter)
solve(r::Rule{Not}, letter) = !solve(r.A, letter)
solve(r::Rule{Letter}, letter) = solve(r.A, letter)

found = String[]

isnot(fact::AbstractString) = fact[1] == '!'

invert(fact::AbstractString) = isnot(fact) ? fact[2:2] : "!" * string(fact) 

function solve(fact::AbstractString, unknown=AbstractString[])
    verbose && @info "Trying to solve $fact"
    if occursin(fact, inputs)
        verbose && @info "\t$fact => is input"
        true
    elseif fact in found
        verbose && @info "\t$fact => Already found that it's true"
        true
    elseif invert(fact) in found
        false
    elseif fact in unknown
        @warn "\t$fact => Circular dependecy"
        fact[1] == '!'
    elseif haskey(letters, fact)
        for rule in letters[fact]
            verbose && @info "\t$rule => $fact"
            if solve(rule, push!(unknown, fact))
                verbose && @info "\t$fact is true"
                push!(found, fact)
                return true
            end
            pop!(unknown)
        end
        verbose && @info "\tNo rules validated for $fact"
        false
    elseif haskey(letters, invert(fact))
        for rule in letters[invert(fact)]
            verbose && @info "\t$rule => $(invert(fact))"
            if solve(rule, push!(unknown, invert(fact)))
                verbose && @info "\t$(invert(fact)) is true so $fact is false"
                push!(found, invert(fact))
                return false
            end
            pop!(unknown)
        end
        verbose && @info "\tNo rules validated for $(invert(fact))"
        true
    else
        verbose && @info "\tNo rules found for $fact"
        fact[1] == '!'
    end
end

function solve_outputs(; verbose=false)
    for letter in outputs
        result = solve(string(letter))
        global current_letter = letter
        verbose && @info "Checking contradictions"
        if solve("!" * string(letter)) == result == true
            myerror("Contradictions in the rules")
        end

        @info "banane"
        println("$letter = $result")
    end
    global found = String[]
    nothing
end

function main()
    if length(ARGS) < 1 || length(ARGS) > 3
        myerror("usage: julia ExpertSystem.jl file.txt [--verbose] [--interactive]")
    end
    if "--verbose" in ARGS[2:end]
        global verbose = true
    end
    parse_file(ARGS[1])
    solve_outputs()
    if "--interactive" in ARGS[2:end]
        while true
            line = readline()
            if length(line) >= 1
                if line[1] == '=' && all(isuppercase, line[2:end])
                    global inputs = line[2:end]
                elseif line[1] == '?' && all(isuppercase, line[2:end])
                    global outputs = line[2:end]
                elseif line in ["q", "quit", "exit"]
                    exit(0)
                elseif line in ["v", "verbose"]
                    global verbose = !verbose
                    println("Verbose: $verbose")
                    continue
                else
                    println("=XXX to change input, ?XXX to change output, v for changing verbose, q to quit")
                    continue
                end
            end
            solve_outputs()
        end
    end
end
main()