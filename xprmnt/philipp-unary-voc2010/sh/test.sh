#!/bin/sh
# if [ "$#" -ne 1 ]; then
#     echo "Illegal number of parameters"
#     exit 1
# fi
curr_dir="$(dirname "$0")"

# Constant params across num
exe=../cc/build/main
root_dir=/home/tor/sun4/xprmnt/own-unary-voc2010
. "$curr_dir/set_dataset_param.sh"

# Varied params
# num=$1
result_dir=$root_dir/annotation/with-own-unaries-20141218/split_voc2010_philipp_Test_csv/
test_img_list_filepath=$root_dir/meta/split_voc2010_philipp/Test.901.txt

# Annotate
#rm -rf $result_dir
#mkdir -p $result_dir
$exe $dataset_name $n_label $ori_img_dir $test_img_list_filepath $result_dir $unary_philipp_dir
