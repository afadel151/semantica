<script setup lang="ts">
</script>

<template>
    <Table>
        <TableHeader>
            <TableRow>
                <TableHead>Class URI</TableHead>
                <TableHead>Prefix form</TableHead>
                <TableHead>Parent class</TableHead>
                <TableHead>Children count</TableHead>
                <TableHead>Individuals count</TableHead>
                <TableHead>Is Abstract</TableHead>
                <TableHead>Depth in hierarchy</TableHead>
            </TableRow>
        </TableHeader>
          <TableBody>
            <TableRow>
                <TableCell>http://xmlns.com/foaf/0.1/Person</TableCell>
                <TableCell>foaf:Person</TableCell>
                <TableCell>foaf:Agent</TableCell>
                <TableCell>3</TableCell>
                <TableCell>12</TableCell>
                <TableCell>True</TableCell>
                <TableCell>2</TableCell>
            </TableRow>
             <TableRow>
                <TableCell>http://xmlns.com/foaf/0.1/Person</TableCell>
                <TableCell>foaf:Person</TableCell>
                <TableCell>foaf:Agent</TableCell>
                <TableCell>3</TableCell>
                <TableCell>12</TableCell>
                <TableCell>True</TableCell>
                <TableCell>2</TableCell>
            </TableRow>
            <TableRow>
                <TableCell>http://xmlns.com/foaf/0.1/Person</TableCell>
                <TableCell>foaf:Person</TableCell>
                <TableCell>foaf:Agent</TableCell>
                <TableCell>3</TableCell>
                <TableCell>12</TableCell>
                <TableCell>True</TableCell>
                <TableCell>2</TableCell>
            </TableRow>
          </TableBody>
    </Table>
</template>