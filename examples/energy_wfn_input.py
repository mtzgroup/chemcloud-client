from qcio import ProgramInput, Structure

from chemcloud import compute

water = Structure(
    symbols=["O", "H", "H"],
    geometry=[
        [0.0000, 0.00000, 0.0000],
        [0.2774, 0.89290, 0.2544],
        [0.6067, -0.23830, -0.7169],
    ],
)


prog_inp = ProgramInput(
    calctype="energy",
    structure=water,
    model={"method": "b3lyp", "basis": "6-31g"},
    keywords={"guess": "c0"},
    files={
        "c0": b'\xdf4R\xdea\xd7\xef?\xc1-\xbdg2\xd0\xca?\x8e\xc4\x94\x02\xe5\xcd\xae\xbe\xd9kP\xd8R2\xb7\xbfhV\xc1\x136\xe5\xbe\xbe\xad\x0b#2\xabp\xb6?\xe9\x91\x99\xbf\xd7\xe9e>LQ\x05\xa4F\xaa\xa6>>k\xab\xa4\xd4j\xa1\xbf\xd1#\xbf\x14\t\xdf\xd8>\x99Qq\x1b\x07\x0b\xb4?$*\x0ed\x95\x91\x97\xbe\r\xc8\xfb\xca\xbb\x82\xab?\'d\x0c-Y\x8e\x9c?\x8c\x10\xf1\xd9I\xb5\xdd\xbf\xf7\xea%X\xd0\x02\xbf>==urA\xc8\xc9?\xe0f\xbb#^\t\xc8>\xe3\xfb\x8b\xc2C\x94\xc3\xbf\xd0]m\x85\xd1\xd7\xb5>\xa2\x1c\x03Un0\xd6\xbe\xc1\x90\xb8\xec\n"\xc9??\xd3\x90\x80q\xeb\x06\xbf,\xa9\x0f\xc0\x8dZ\xdf\xbf% \xcc\x86L\x85\xc2\xbe\xdf\xae\xb07\xe4\x91\xfa\xbf\xa9\x97q\x07\xff\xd0\x8a\xbf\x04\xad\xabq\xc8\xed\xdc\xbf\xb3]B\x0c\xcc\xa4\xca>\x00\xaaX\xed\xd7\xe9\xd7?\xa5\xbf\xc0\x05O\xb2\xe1>>c\x1f\xef\x924\xf1\xbf\xf9\xac0\xe1r-\xcf\xbe\xe3]\x92[g\x18\xe4>Zm8\x07@\xbd\xd2\xbf\xae\x86\xa3\x19Hl\x0b?e\xb2\x81\xdd\xdbz\xc0?\xc04\xaea,1\xe0>t&x\xceH\xf5\x05@\xc7\'\xb0\xb9\xd1g#?\x82Hm\x14\xba\x14\xc3\xbfT\x19p\xa8T\x00\xd1?\xc5 \xfc\xae\xabf\xc2\xbfm2\xf0t\xde\x84\xd0\xbe#(\x16bTh\xb9?\xd7i&\x01\xc8\xb7\xb9?\x02\xdc\xe5m\xea\n\xef\xbf\xf6\xfb\x86\n\x97O\xe7\xbfX\xe7\xdfb\x00\xb8\x1d?\x19!\x83a\xb5\xeb\xe4?\xa5\x0b\xf5>wJ\x9e?\xcf\xdb\x884z\xee\xde\xbf\xea\xbf\xa7\xd3@\xd7h?F5\x9b\x1f\x93"@\xbf/\x8d\x1e.\x84o\xc3?\x08!\xa9\\\xc5d\xbb\xbf=\x18s\x1a\xf6\xa3\xd2\xben\xf7\x8e\xb5B\xbe\xed?\x96\xd0:\xeb\xbdI\xf4?\xa1b\x81\x15QU\xe6?7\xf1\xb6\xac\xd4i\xe3?\xc2\xf35\x18\xc7\x90\x10\xbf\xc4 \xf3\xe5\x93\x94\xc6\xbfE\x96\xe1\xa1\xb2\xe6\xec?b\xf4\xd8K\x1a|\xe3\xbf\xabKE\x9a+g#?I>t\xa1\xc7\x14\xc3\xbfM\xd7\x13\xb7V\x00\xd1\xbf\xc4\x1e\xf1\x02\xa1f\xc2\xbf\x16\x8d\x03l\xd3\x8e\xa6\xbe\xdd$uFwh\xb9?\xcap6\x18\xfd\xb7\xb9\xbf|\xff&\xa8/\x0b\xef?\x8c+\x9eG0O\xe7\xbf\xf6\xfd$\x1eY\xdc\x15?4L\x99\xf7\xbd\xeb\xe4?\xdd=\xbaD\xdbM\x9e\xbff\x04*Q\x81\xee\xde\xbfZ\x12\x87\x8eF\xd7h?\n6\xbd1\x84&@\xbf \xbd#\x84\x88o\xc3\xbf\xf2\x9bj\x08\x9dd\xbb\xbf\xcc\x90aR\xded\xb8>\x18\xcd\t\xf5H\xbe\xed?\xdaw\x8a\xa3\xb6I\xf4\xbf\t\xe3\xf8\xf0\x92U\xe6\xbf\x83\xe8\x9d\x93\xadi\xe3?p\x0bF\xfe\x9a\x11\x18\xbf\xd9A\xc7g\xc4\x94\xc6\xbf\x8e\xdd\xeb\xa4\xb0\xe6\xec\xbfJ\xb6@\xbb\x15|\xe3\xbf\x08\xe1\xfa\xa9\xc0\xb1Z?\xf2\x88\x88!\xff\xaa\xbc\xbf[.\xb8e\xa8x\xbc\xbf\x07\x90nr\xb8\xc3\xd9\xbf4\x99\xf9\x99\x80Q\xda\xbf\x05\xd8$t\x9e\xfc\xcb\xbf\xf5\xfe|\xa6gH\xb7?\xbf\x0e\xb8L@V\xa6\xbf\xc8\xa2\x05\x84\xba\x05\xe2?\xa2I\xa0\x1f\x9f\x80\xe3\xbfGv\xefeG\\\xdc?\xeb\x18\xd63\xc1\x19\xcb\xbfW"\xb9\x87P\x92\xc1\xbf\x05\x13\xa3IY\xc3S?\xa8\xa2\x18?\x0e9\xb5\xbf \xd9\xcbJNq\xd8?x\xa8\xa4/6\x13\xd3\xbf\xbdLJA\xcc\n\xd0?\xb6i\xb5\x01\x1b\xb8\xc4\xbf\xa7eF\xef.\xfd\xd3\xbf\rf\x06.Z*\xc3?\x0b\xaf\xbb\xe4\xe1\xb0\xda?u\x91\xb0I\x9d\xc5\xd7?^\x9c\xffh\xa3\xfe\xd4?\xdf\x0ec\xf3\xc0D\xe7?`\xd6\xfb\xfd\xf3\x04\xba\xbf\x8c\xf1\xcd\x98\x93\xedK\xbfv"!\xed\x91\xfd\xad?ey\xdd\x08\xc5\xfc\xd4?r\xb7>\\\x83\xf4\xca?\x84M\xaf\x8f\xbb\x9b\xdb\xbfk\xa36\xd6UG\xbd?\xd9\xfd\x0f\x18\xdb)\xd1\xbf\xfb`\x8e\xf0\xf0t\xc0?9\x1f\x0b\xb9h\xdc\xd2\xbf\xadk\t_\xa5t\xe4\xbf\xc1dH\r`\xaa\xcd\xbf\xb8\xbe\xa9n\xea\xfa\xe3?\xaa\x927\x94 b\xb2?\'\x84E8\x0e\x84`\xbf\xcf\xc9\xaa$\xae\xaf\xaa\xbf\xefb}_82\xaa\xbf\xd4\xfeS\xc3N\xc0\xd1\xbf\xdf\xd5k\x1b\x08\x8b\xd4\xbf\xcf\x02\xa6\xe9\xaa=\xd5\xbfLI\xad\x02m\xb6\xc4?\xe9=\x13\xecr\xe2\xba\xbf\xd4\xf5\x91\xd75\xfb\xd5\xbfa\xaa\xb0\x86S*\xe5?#\x92\xd8\x85\x1f\x8d\xea\xbf\x04\x8e\xfa\xde\xe4\xf1\xd6?\xdd\xf3\xc8[.\xc9\xe4?\xae\xef\x9f\x01{tX\xbf\xfdG\xb1\xd6\xa1\xc1\xa3\xbfe\xa4\xa5\xacy}\xc6?/\xe3>s\xcfH\xca\xbf\xb4\xe7\xd4\xf9\x0e\x0b\xc9?\xe0\xf7\xf8B]s\xcf\xbf/$\x91\x9dh\xc8\xe1\xbfk\xa6\x86\xed\xfd\x15\xd7?\x9fo\xed~OG\xd0\xbft9\xe6\xcd\xa9\xcd\xd9\xbfa\xa6>"\xeb\xa7\xe3\xbfj?\xea\xd6\x11\xb3\xf3\xbf\xf2=JS\xf6\xc6\xde?9BT]PGQ?\xe9\x80\xd0\x08\xfe\xea\x9b?\xf5G\xb1\x83\xa0O\xc3?\xef\x96y[9\x92\xc2?\xc7\xb6\xd7\x87\xce\x8c\xd5\xbf\xd1Q\x02l\x958\xc6?C\xd8\x13\x1c\xdb\x89\xde\xbf2\x02y\'\xa4\xd2\xd3?^\xef\x1f\xd70\x03\xc7?\xacm2\x05s3\xe6?\xc0\xde\x00pP\xc6\xdb?\x0fx\x8c\xdfP\xea\xf0\xbf\xa7\xd4\x80E\xc9\xbe\xd5\xbf'  # noqa: E501
    },
)
output = compute("terachem", prog_inp)
# ProgramOutput object containing all returned data
print(output.stdout)
print(output)
# The energy value requested
print(output.results.energy)
# Not empty if collect_files=True passed to compute
print(output.results.files.keys())
