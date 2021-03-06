from coderunner import *

header("Instantiation")

test(Scala,
"""
trait Foo{
  def foo() = println("foo!")
}

new Foo  // error
""",  """
...tmp.scala:5: error: trait Foo is abstract; cannot be instantiated
new Foo  // error
^
one error found
""")


test(Squeak,
"""
Trait named: #Foo
    uses: {}
    category: #MyCategory.

print value:(Foo new).
""",  """
a Foo
""")

comment('Oops, trait in Squeak can be instanciated...')


test(Ruby,
"""
module Foo end

Foo new
""",  """
tmp.rb:3:in `<main>': undefined local variable or method `new' for main:Object (NameError)
""")


header('Single inheritance')

test(Scala,
"""
trait Foo{
  def foo() = println("foo!")
}

class C extends Foo{}
new C().foo
""",  """
foo!
""")


test(Squeak,
"""
Trait named: #Foo
    uses: {}
    category: #MyCategory.

Foo compile: '
foo
    ^''foo''
'.

Object subclass: #C
    uses: Foo
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: #MyCategory.

print value: (C new foo).
""",  """
foo
""")

test(Ruby,
"""
module Foo
  def foo
    puts "foo"
  end
end

class C
  include Foo
end

C.new.foo
""",  """
foo
""")


header('Multiple inheritance')

test(Scala,
"""
trait Foo{
  def foo() = println("foo!")
}

trait Bar{
  def bar() = println("bar!")
}

class C extends Foo with Bar{}
new C().foo
new C().bar
""",  """
foo!
bar!
""")


test(Squeak,
"""
Trait named: #Foo
    uses: {}
    category: #MyCategory.

Foo compile: '
foo
    ^''foo''
'.

Trait named: #Bar
    uses: {}
    category: #MyCategory.

Bar compile: '
bar
    ^''bar''
'.

Object subclass: #C
    uses: Foo + Bar
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: #MyCategory.

print value: (C new foo).
print value: (C new bar).
""",  """
foo
bar
""")

test(Ruby,
"""
module Foo
  def foo
    puts "foo"
  end
end

module Bar
  def bar
    puts "bar"
  end
end

class C
  include Foo
  include Bar
end

C.new.foo
C.new.bar
""",  """
foo
bar
""")

header('Conflicting name')

test(Scala,
"""
trait Foo{
  def hello() = println("foo!")
}

trait Bar{
  def hello() = println("bar!")
}

class C extends Foo with Bar{}
""",  """
...tmp.scala:9: error: class C inherits conflicting members:
  method hello in trait Foo of type ()Unit  and
  method hello in trait Bar of type ()Unit
(Note: this can be resolved by declaring an override in class C.)
class C extends Foo with Bar{}
      ^
one error found
""")


test(Squeak,
"""
Trait named: #Foo
    uses: {}
    category: #MyCategory.

Foo compile: '
hello
    ^''foo''
'.

Trait named: #Bar
    uses: {}
    category: #MyCategory.

Bar compile: '
hello
    ^''bar''
'.

Object subclass: #C
    uses: Foo + Bar
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: #MyCategory.

[
    print value: (C new hello).
] on: Exception
  do: printException.
""",  """
Error: A class or trait does not properly resolve a conflict between multiple traits it uses.
""")

comment('error occurs when you send a message, not when you define a class')


test(Ruby,
"""
module Foo
  def hello
    puts "foo"
  end
end

module Bar
  def hello
    puts "bar"
  end
end

class C
  include Foo
  include Bar
end

C.new.hello
""",  """
bar
""")

comment("Ruby silently overrides conflicting methods")


header('Choose one of the methods')
test(Scala,
"""
trait Foo{
  def hello() = println("foo!")
}

trait Bar{
  def hello() = println("bar!")
}

class C extends Foo with Bar{
  override def hello() = super[Bar].hello
}

new C().hello
""",  """
bar!
""")


test(Squeak,
"""
Trait named: #Foo
    uses: {}
    category: #MyCategory.

Foo compile: '
hello
    ^''foo''
'.

Trait named: #Bar
    uses: {}
    category: #MyCategory.

Bar compile: '
hello
    ^''bar''
'.

Object subclass: #C
    uses: Foo - {#hello} + Bar
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: #MyCategory.

print value: (C new hello).
""",  """
bar
""")

test(Ruby,
"""
module Foo
  def hello
    puts "foo"
  end
end

module Bar
  def hello
    puts "bar"
  end
end

class C
  include Bar
  include Foo
  def hello
    Bar.instance_method(:hello).bind(self).call
  end
end

C.new.hello
""",  """
bar
""")


header('Use both of the methods')

test(Scala,
"""
trait Foo{
  def hello() = println("foo!")
}

trait Bar{
  def hello() = println("bar!")
}

class C extends Foo with Bar{
  override def hello() = {  // use both
    super[Foo].hello
    super[Bar].hello
  }
}

new C().hello
""",  """
foo!
bar!
""")

test(Squeak,
"""
Trait named: #Foo
    uses: {}
    category: #MyCategory.

Foo compile: '
hello
    ^''foo''
'.

Trait named: #Bar
    uses: {}
    category: #MyCategory.

Bar compile: '
hello
    ^''bar''
'.

Object subclass: #C
    uses: (Foo @ {#foo -> #hello} - {#hello} +
           Bar @ {#bar -> #hello} - {#hello})
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: #MyCategory.

C compile: '
hello
    ^(self foo , self bar)
'.

print value: (C new hello).
""",  """
foobar
""")

test(Ruby,
"""
module Foo
  def hello
    puts "foo"
  end
end

module Bar
  def hello
    puts "bar"
  end
end

class C
  include Foo
  include Bar
  def hello
    Foo.instance_method(:hello).bind(self).call
    Bar.instance_method(:hello).bind(self).call
  end
end

C.new.hello
""",  """
foo
bar
""")


header('required trait(self type annotation of Scala)')

test(Scala,
"""
trait HaveFoo{
  def foo() : String = "foo"
}

trait NeedFoo{
  self : HaveFoo =>
  def hello() = println(foo())
}

// error: NeedFoo should be with HaveFoo
class C extends NeedFoo{}
""",  """
...tmp.scala:11: error: illegal inheritance;
 self-type this.C does not conform to this.NeedFoo's selftype this.NeedFoo with this.HaveFoo
class C extends NeedFoo{}
                ^
one error found
""")

test(Scala,
"""
trait HaveFoo{
  def foo() : String = "foo"
}

trait NeedFoo{
  self : HaveFoo =>
  def hello() = println(foo())
}

class C extends NeedFoo with HaveFoo{}
new C().hello
""",  """
foo
""")


header('conflict between parent class and trait')

test(Scala,
"""
trait Foo{
  def hello() = println("foo!")
}

class ParentClass{
  def hello() = println("parent class!")
}

class C extends ParentClass with Foo{}
""",  """
...tmp.scala:9: error: class C inherits conflicting members:
  method hello in class ParentClass of type ()Unit  and
  method hello in trait Foo of type ()Unit
(Note: this can be resolved by declaring an override in class C.)
class C extends ParentClass with Foo{}
      ^
one error found
""")

test(Squeak,
"""
Trait named: #Foo
    uses: {}
    category: #MyCategory.

Foo compile: '
hello
    ^''foo''
'.

Object subclass: #ParentClass
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: #MyCategory.

ParentClass compile: '
hello
    ^''parent class''
'.

ParentClass subclass: #C
    uses: Foo
    instanceVariableNames: ''
    classVariableNames: ''
    poolDictionaries: ''
    category: #MyCategory.


print value: (C new hello).
""",  """
foo
""")

test(Ruby,
"""
module Foo
  def hello
    puts "foo"
  end
end

class ParentClass
  def hello
    puts "parent class"
  end
end

class C < ParentClass
  include Foo
end

C.new.hello
""",  """
foo
""")

main()
