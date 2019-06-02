function check_basic_op(str::AbstractString, op_char::AbstractChar, index::Integer)
    parentheses = 0
    for (i, letter) in enumerate(str)
        if parentheses == 0 && letter == op_char
            return Rule{op_type[op_char]}(str[1:i - 1], str[i + 1:end], index)
        elseif letter == '('
            parentheses += 1
        elseif letter == ')'
            parentheses -= 1
            if parentheses < 0
                myerror("Too many ) at line " * string(index))
            end
        end
    end
    if parentheses != 0
        myerror("Too many ( at line " * string(index))
    end
    nothing
end

function check_parentheses_op(str::AbstractString, index::Integer)
    parentheses = 0
    first = 1
    for (i, letter) in enumerate(str)
        if letter == '('
            if parentheses == 0
                first = i
            end
            parentheses += 1
        elseif letter == ')'
            parentheses -= 1
            if parentheses == 0
                if all(isspace, str[1:first - 1] * str[i + 1:end])
                    return get_rule(str[first + 1:i - 1], index)
                elseif all(isspace, str[1:first - 2] * str[i + 1:end]) && str[first - 1] == '!'
                    return Rule{Not}(str[first + 1:i - 1], index)
                else
                    myerror("Wrong character at line " * string(index))
                end
            end
        end
    end
    nothing
end

function check_letter(str::AbstractString)
    for (i, letter) in enumerate(str)
        if letter == '!' && isuppercase(str[i + 1]) && all(isspace, str[1:i - 1] * str[i + 2:end])
            return Rule(str[i:i + 1])
        elseif isuppercase(letter) && all(isspace, str[1:i - 1] * str[i + 1:end])
            return Rule(str[i:i])
        end
    end
end

function get_rule(str::AbstractString, index::Integer)
    if (rule = check_basic_op(str, '^', index)) != nothing
        return rule
    end
    if (rule = check_basic_op(str, '|', index)) != nothing
        return rule
    end
    if (rule = check_basic_op(str, '+', index)) != nothing
        return rule
    end
    if (rule = check_parentheses_op(str, index)) != nothing
        return rule
    end
    if (rule = check_letter(str)) != nothing
        return rule
    end
    myerror("Can't parse a rule at line " * string(index))
end

function get_letters(line::AbstractString, index::Integer)
    letters = AbstractString[]
    for str in split(line, "+")
        for (i, c) in enumerate(str)
            if isuppercase(c)
                if all(isspace, str[1:i - 1] * str[i + 1:end])
                    push!(letters, str[i:i])
                    break
                else
                    myerror("Wrong character at line " * string(index))
                end
            elseif c == '!' && isuppercase(str[i + 1])
                if all(isspace, str[1:i - 1] * str[i + 2:end])
                    push!(letters, str[i:i + 1])
                    break
                else
                    myerror("Wrong character at line " * string(index))
                end
            end
        end
    end
    if length(letters) == 0
        myerror("No valid letter in the conclusion of the rule at line " * string(index))
    end
    letters
end 

function split_line(line::AbstractString, index::Integer)
    splitted = split(line, "=>")
    if length(splitted) != 2
        myerror("Can't parse a rule at line " * string(index))
    end
    rule = get_rule(splitted[1], index)
    for letter in get_letters(splitted[2], index)
        if !haskey(letters, letter)
            letters[letter] = Rule[]
        end
        push!(letters[letter], rule)
    end
end

function check_inputs_outputs(line::AbstractString)
    if line[1] == '='
        endline = findfirst(isequal(' '), line)
        if endline == nothing
            endline = length(line) + 1
        end
        if inputs != nothing
            myerror("Only one input can be given")
        end
        global inputs = line[2:endline - 1]
        return true
    end
    if line[1] == '?'
        endline = findfirst(isequal(' '), line)
        if endline == nothing
            endline = length(line) + 1
        end
        if outputs != nothing
            myerror("Only one output can be given")
        end
        global outputs = line[2:endline - 1]
        return true
    end
    false
end

function clean_line(line::AbstractString)
    comment_index = findfirst(isequal('#'), line)
    if comment_index == nothing
        comment_index = length(line) + 1
    end
    if comment_index == 1
        return nothing
    end
    line = line[1:comment_index - 1]
    if all(isspace, line)
       return nothing
    end
    if check_inputs_outputs(line)
        return nothing
    end
    line
end